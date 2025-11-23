from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
import json
import uuid

from .models import Agreement, AgreementType, Photo
from .openai_service import get_chat_response, generate_agreement


def landing(request):
    """Step 1: Landing page"""
    return render(request, 'landing.html')


def select_type(request):
    """Step 2: Choose agreement type"""
    if request.method == 'POST':
        # Create new agreement session
        session_key = str(uuid.uuid4())
        request.session['agreement_session'] = session_key
        
        type_id = request.POST.get('agreement_type')
        agreement_type = get_object_or_404(AgreementType, id=type_id)
        
        # Create agreement
        agreement = Agreement.objects.create(
            agreement_type=agreement_type,
            session_key=session_key,
            status='reflection'
        )
        
        return redirect('reflection')
    
    types = AgreementType.objects.all()
    return render(request, 'select_type.html', {'types': types})


def reflection(request):
    """Step 3: Conversational reflection with AI"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('select_type')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    return render(request, 'reflection.html', {
        'agreement': agreement,
        'agreement_type': agreement.agreement_type.name
    })


@csrf_exempt
def chat_api(request):
    """API endpoint for chat messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    session_key = request.session.get('agreement_session')
    if not session_key:
        return JsonResponse({'error': 'No session'}, status=400)
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    data = json.loads(request.body)
    user_message = data.get('message', '')
    
    # Add user message to history
    if not agreement.conversation_history:
        agreement.conversation_history = []
    
    agreement.conversation_history.append({
        'role': 'user',
        'content': user_message
    })
    
    # Get AI response
    ai_response = get_chat_response(agreement.conversation_history)
    
    # Add AI response to history
    agreement.conversation_history.append({
        'role': 'assistant',
        'content': ai_response
    })
    
    agreement.save()
    
    return JsonResponse({
        'response': ai_response,
        'message_count': len(agreement.conversation_history)
    })


def generate_agreement_view(request):
    """Generate agreement from conversation"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('select_type')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    # Extract participants from conversation if not set
    if not agreement.participants:
        # Simple extraction - could be improved
        for msg in agreement.conversation_history:
            if msg['role'] == 'user' and 'between' in msg['content'].lower():
                agreement.participants = msg['content']
                break
        if not agreement.participants:
            agreement.participants = "Participants"
    
    # Generate agreement text
    agreement.agreement_text = generate_agreement(
        agreement.conversation_history,
        agreement.agreement_type.name,
        agreement.participants
    )
    agreement.status = 'review'
    agreement.save()
    
    return redirect('review')


def review(request):
    """Step 4: Review and edit agreement"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('select_type')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    if request.method == 'POST':
        edited_text = request.POST.get('agreement_text')
        agreement.edited_text = edited_text
        agreement.status = 'signed'
        agreement.save()
        return redirect('print_agreement')
    
    return render(request, 'review.html', {
        'agreement': agreement,
        'agreement_text': agreement.get_final_text()
    })


def print_agreement(request):
    """Step 5: Print agreement"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('select_type')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    if request.method == 'POST':
        agreement.signed_at = timezone.now()
        agreement.save()
        return redirect('photo')
    
    return render(request, 'print.html', {
        'agreement': agreement,
        'agreement_text': agreement.get_final_text()
    })


def photo(request):
    """Step 6: Upload photo of signing"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('select_type')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    if request.method == 'POST':
        # Check for base64 photo data (from camera)
        photo_data = request.POST.get('photo_data')
        
        if photo_data:
            # Handle base64 camera photo
            import base64
            from django.core.files.base import ContentFile
            from datetime import datetime
            
            # Remove data URL prefix
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Create file from base64
            photo_file = ContentFile(
                base64.b64decode(imgstr),
                name=f'signing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
            )
            
            Photo.objects.create(
                agreement=agreement,
                image=photo_file
            )
        elif request.FILES.get('photo'):
            # Handle uploaded file
            Photo.objects.create(
                agreement=agreement,
                image=request.FILES['photo']
            )
        else:
            return render(request, 'photo.html', {
                'agreement': agreement,
                'error': 'Please capture or upload a photo'
            })
        
        agreement.status = 'completed'
        agreement.completed_at = timezone.now()
        agreement.save()
        return redirect('complete')
    
    return render(request, 'photo.html', {'agreement': agreement})


def complete(request):
    """Step 7: Completion - envelope moment"""
    session_key = request.session.get('agreement_session')
    if not session_key:
        return redirect('landing')
    
    agreement = get_object_or_404(Agreement, session_key=session_key)
    
    # Clear session after completion
    if 'agreement_session' in request.session:
        del request.session['agreement_session']
    
    return render(request, 'complete.html', {
        'agreement': agreement,
        'participants': agreement.participants
    })


@staff_member_required
def archive(request):
    """Step 8: Exhibition archive (admin only)"""
    agreements = Agreement.objects.filter(
        status='completed',
        is_archived=True
    ).select_related('agreement_type')
    
    return render(request, 'archive.html', {
        'agreements': agreements,
        'total_count': agreements.count()
    })