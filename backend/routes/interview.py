from flask import Blueprint, request, jsonify
import sys
import os

# Add the parent directory to the Python path to access ribbon module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ribbon.ribbon_client import RibbonClient, InterviewFlow, InterviewConfig
except ImportError:
    # Fallback import for different module structure
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ribbon'))
        from ribbon_client import RibbonClient, InterviewFlow, InterviewConfig
    except ImportError as e:
        print(f"Warning: Could not import ribbon client: {e}")
        RibbonClient = None

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/create-flow', methods=['POST'])
def create_interview_flow():
    """Create a new interview flow"""
    try:
        if RibbonClient is None:
            return jsonify({"error": "Ribbon client not available. Please check your environment setup."}), 503
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['org_name', 'title', 'questions']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create InterviewFlow object
        flow = InterviewFlow(
            org_name=data['org_name'],
            title=data['title'],
            questions=data['questions'],
            interview_type=data.get('interview_type', 'general'),
            voice_id=data.get('voice_id', '11labs-Kate'),
            language=data.get('language', 'en-US'),
            company_logo_url=data.get('company_logo_url'),
            additional_info=data.get('additional_info'),
            is_video_enabled=data.get('is_video_enabled', False),
            is_phone_call_enabled=data.get('is_phone_call_enabled', True),
            is_doc_upload_enabled=data.get('is_doc_upload_enabled', False),
            redirect_url=data.get('redirect_url'),
            webhook_url=data.get('webhook_url')
        )
        
        # Create the flow using Ribbon client
        client = RibbonClient()
        result = client.create_interview_flows([flow])
        
        return jsonify({
            "success": True,
            "flow_id": flow.interview_flow_id,
            "message": "Interview flow created successfully",
            "data": result
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create interview flow: {str(e)}"}), 500


@interview_bp.route('/create-interview', methods=['POST'])
def create_interview():
    """Create a new interview from an existing flow"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'interview_flow_id' not in data:
            return jsonify({"error": "Missing required field: interview_flow_id"}), 400
        
        # Create InterviewConfig object
        config = InterviewConfig(
            interview_flow_id=data['interview_flow_id'],
            interviewee_email_address=data.get('interviewee_email_address'),
            interviewee_first_name=data.get('interviewee_first_name'),
            interviewee_last_name=data.get('interviewee_last_name')
        )
        
        # Create the interview using Ribbon client
        client = RibbonClient()
        result = client.create_interview(config)
        
        return jsonify({
            "success": True,
            "interview_id": result.get('interview_id'),
            "interview_link": result.get('interview_link'),
            "message": "Interview created successfully",
            "data": result
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create interview: {str(e)}"}), 500


@interview_bp.route('/interview/<interview_id>', methods=['GET'])
def get_interview(interview_id):
    """Get interview details and results"""
    try:
        client = RibbonClient()
        interview_data = client.get_interview(interview_id)
        
        return jsonify({
            "success": True,
            "data": interview_data
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve interview: {str(e)}"}), 500


@interview_bp.route('/interview/<interview_id>/status', methods=['GET'])
def get_interview_status(interview_id):
    """Get interview status"""
    try:
        client = RibbonClient()
        status = client.get_interview_status(interview_id)
        
        return jsonify({
            "success": True,
            "interview_id": interview_id,
            "status": status
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get interview status: {str(e)}"}), 500


@interview_bp.route('/interview/<interview_id>/transcript', methods=['GET'])
def get_interview_transcript(interview_id):
    """Get interview transcript"""
    try:
        client = RibbonClient()
        transcript = client.get_interview_transcript(interview_id)
        
        if transcript is None:
            return jsonify({
                "success": False,
                "message": "Interview not completed yet or transcript not available"
            }), 404
        
        return jsonify({
            "success": True,
            "interview_id": interview_id,
            "transcript": transcript
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get interview transcript: {str(e)}"}), 500


@interview_bp.route('/interview/<interview_id>/audio', methods=['GET'])
def get_interview_audio(interview_id):
    """Get interview audio URL"""
    try:
        client = RibbonClient()
        audio_url = client.get_interview_audio_url(interview_id)
        
        if audio_url is None:
            return jsonify({
                "success": False,
                "message": "Interview not completed yet or audio not available"
            }), 404
        
        return jsonify({
            "success": True,
            "interview_id": interview_id,
            "audio_url": audio_url
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get interview audio: {str(e)}"}), 500


@interview_bp.route('/quick-flow', methods=['POST'])
def create_quick_flow():
    """Create a quick interview flow for stylist consultation"""
    try:
        data = request.get_json()
        
        org_name = data.get('org_name', 'Your Styling Company')
        
        # Stylist consultation template
        template_data = {
            'title': 'Personal Styling Consultation',
            'questions': [
                "What's your current style like and how would you describe your fashion preferences?",
                "What occasions or situations are you looking to dress for?",
                "What are your biggest styling challenges or areas where you'd like recommendations?"
            ],
            'interview_type': 'consultation',
            'additional_info': 'Personal styling consultation to provide tailored fashion recommendations'
        }
        
        # Create InterviewFlow object
        flow = InterviewFlow(
            org_name=org_name,
            title=template_data['title'],
            questions=template_data['questions'],
            interview_type=template_data['interview_type'],
            additional_info=template_data['additional_info']
        )
        
        # Create the flow using Ribbon client
        client = RibbonClient()
        result = client.create_interview_flows([flow])
        
        return jsonify({
            "success": True,
            "template": "stylist_consultation",
            "flow_id": flow.interview_flow_id,
            "message": "Stylist consultation flow created successfully",
            "data": result
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create stylist consultation flow: {str(e)}"}), 500


@interview_bp.route('/templates', methods=['GET'])
def get_available_templates():
    """Get available template information"""
    template = {
        'stylist_consultation': {
            'name': 'Personal Styling Consultation',
            'description': 'Consultation to understand client style preferences and provide personalized recommendations',
            'question_count': 3,
            'type': 'consultation'
        }
    }
    
    return jsonify({
        "success": True,
        "template": template
    })
