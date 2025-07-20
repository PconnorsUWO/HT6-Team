"""
Working Example with Flow Creation and Management

This example demonstrates how to:
1. Create various types of interview flows
2. Work with existing interview flows 
3. Create interviews
4. Retrieve interview results
"""

from ribbon_client import RibbonClient, InterviewConfig, InterviewFlow
import time


def create_sample_interview_flows():
    """Create various types of interview flows for different use cases"""
    client = RibbonClient()
    
    print("🎯 Creating Sample Interview Flows")
    print("=" * 50)
    
    # Define different flow templates
    flows_to_create = [
        {
            "org_name": "wardrobe.ai",
            "title": "Get Dripped or Drowned",
            "questions": [
                "Are the pieces we try on today for any specific ocassion",
                "What are your style goals?",
            ],
            "interview_type": "Styling Appointment",
            "additional_info": "Get Dripped Beyond Belief"
        },
    ]
    
    created_flows = []
    
    for flow_data in flows_to_create:
        try:
            print(f"\n🔧 Creating flow: {flow_data['title']}")
            
            # Create InterviewFlow object
            flow = InterviewFlow(
                org_name=flow_data['org_name'],
                title=flow_data['title'],
                questions=flow_data['questions'],
                interview_type=flow_data['interview_type'],
                additional_info=flow_data.get('additional_info')
            )
            
            # Create the flow
            result = client.create_interview_flows([flow])
            flow_id = result.get('interview_flow_id')
            
            print(f"✅ Successfully created flow: {flow_id}")
            print(f"   Organization: {flow_data['org_name']}")
            print(f"   Type: {flow_data['interview_type']}")
            print(f"   Questions: {len(flow_data['questions'])}")
            
            created_flows.append({
                'flow_id': flow_id,
                'title': flow_data['title'],
                'org_name': flow_data['org_name'],
                'type': flow_data['interview_type'],
                'questions_count': len(flow_data['questions']),
                'flow_object': flow
            })
            
        except Exception as e:
            print(f"❌ Failed to create flow '{flow_data['title']}': {e}")
            if "exceeded" in str(e).lower() or "limit" in str(e).lower():
                print("   💡 Your API plan may have reached the flow creation limit")
                break
    
    return created_flows


def create_custom_interview_flow(org_name: str, title: str, questions: list, interview_type: str = "general", **kwargs):
    """Create a custom interview flow with specified parameters"""
    client = RibbonClient()
    
    print(f"🎯 Creating Custom Interview Flow: {title}")
    print("-" * 50)
    
    try:
        # Create InterviewFlow object
        flow = InterviewFlow(
            org_name=org_name,
            title=title,
            questions=questions,
            interview_type=interview_type,
            **kwargs
        )
        
        # Create the flow
        result = client.create_interview_flows([flow])
        flow_id = result.get('interview_flow_id')
        
        print(f"✅ Successfully created custom flow: {flow_id}")
        print(f"   Organization: {org_name}")
        print(f"   Title: {title}")
        print(f"   Type: {interview_type}")
        print(f"   Questions: {len(questions)}")
        
        # Display questions
        print(f"\n📝 Questions:")
        for i, question in enumerate(questions, 1):
            print(f"   {i}. {question}")
        
        return {
            'flow_id': flow_id,
            'title': title,
            'org_name': org_name,
            'type': interview_type,
            'questions_count': len(questions),
            'flow_object': flow
        }
        
    except Exception as e:
        print(f"❌ Failed to create custom flow: {e}")
        return None


def demonstrate_flow_creation_workflow():
    """Demonstrate a complete flow creation workflow"""
    print("🚀 Complete Flow Creation Workflow")
    print("=" * 60)
    
    # Step 1: Create a simple flow
    print("\n📋 Step 1: Creating a Simple Interview Flow")
    simple_flow = create_custom_interview_flow(
        org_name="Demo Company",
        title="Quick Team Check-in",
        questions=[
            "How are you feeling about your current projects?",
            "What support do you need from the team?",
            "Any blockers or challenges you're facing?",
            "What's going well for you this week?"
        ],
        interview_type="general",
        additional_info="Weekly team check-in interview"
    )
    
    if not simple_flow:
        print("❌ Could not create simple flow. Check your API limits.")
        return None
    
    # Step 2: Test the flow immediately
    print(f"\n🧪 Step 2: Testing the Created Flow")
    test_interview = test_created_flow(simple_flow)
    
    # Step 3: Create a more complex flow
    print(f"\n📋 Step 3: Creating a Complex Interview Flow")
    complex_flow = create_custom_interview_flow(
        org_name="Advanced Corp",
        title="Senior Developer Deep Dive",
        questions=[
            "Describe your most complex technical architecture project.",
            "How do you approach system design for high-scale applications?",
            "Explain your experience with microservices and distributed systems.",
            "How do you handle technical debt in legacy codebases?",
            "Describe your approach to mentoring junior developers.",
            "What's your philosophy on code reviews and quality assurance?",
            "How do you stay current with emerging technologies?",
            "Tell me about a time you had to make a critical technical decision under pressure."
        ],
        interview_type="recruitment",
        additional_info="Senior level technical assessment",
        is_video_enabled=True,  # Advanced feature
        is_doc_upload_enabled=True  # For portfolio/code samples
    )
    
    return {
        'simple_flow': simple_flow,
        'complex_flow': complex_flow,
        'test_interview': test_interview
    }


def test_created_flow(flow_data):
    """Test a newly created flow by creating a sample interview"""
    if not flow_data:
        return None
        
    client = RibbonClient()
    flow_id = flow_data['flow_id']
    
    print(f"🧪 Testing Flow: {flow_data['title']} ({flow_id})")
    
    try:
        # Create a test interview
        config = InterviewConfig(
            interview_flow_id=flow_id,
            interviewee_email_address="test@example.com",
            interviewee_first_name="Test",
            interviewee_last_name="User"
        )
        
        interview = client.create_interview(config)
        interview_id = interview.get('interview_id')
        interview_link = interview.get('interview_link')
        
        print(f"✅ Test interview created successfully!")
        print(f"   Interview ID: {interview_id}")
        print(f"   Interview Link: {interview_link}")
        
        return {
            'interview_id': interview_id,
            'interview_link': interview_link,
            'flow_id': flow_id
        }
        
    except Exception as e:
        print(f"❌ Failed to create test interview: {e}")
        return None


def list_existing_flows():
    """Try to get information about existing flows by creating test interviews"""
    client = RibbonClient()
    
    print("🔍 Testing with some flow IDs from our previous tests...")
    
    # These are flow IDs that were created during our testing
    test_flow_ids = [
        "4a8eeced",  # From our first successful test
        "ed0b3fe3",  # From our example test
        "63864faf"   # From our minimal test
    ]
    
    working_flows = []
    
    for flow_id in test_flow_ids:
        try:
            # Try to create a test interview to see if the flow exists
            config = InterviewConfig(
                interview_flow_id=flow_id,
                interviewee_email_address="test@example.com",
                interviewee_first_name="Test",
                interviewee_last_name="User"
            )
            
            interview = client.create_interview(config)
            interview_id = interview.get('interview_id')
            
            print(f"✅ Flow {flow_id} is working!")
            print(f"   Created test interview: {interview_id}")
            print(f"   Interview link: {interview.get('interview_link')}")
            
            working_flows.append({
                'flow_id': flow_id,
                'test_interview_id': interview_id,
                'test_interview_link': interview.get('interview_link')
            })
            
        except Exception as e:
            if "403" in str(e):
                print(f"❌ Flow {flow_id} doesn't exist or doesn't belong to this account")
            elif "422" in str(e):
                print(f"❌ Flow {flow_id} not found")
            else:
                print(f"❌ Error testing flow {flow_id}: {e}")
    
    return working_flows


def demonstrate_interview_management(flow_data):
    """Demonstrate interview creation and management"""
    client = RibbonClient()
    flow_id = flow_data['flow_id']
    
    print(f"\n🎤 Creating Multiple Interviews for Flow: {flow_id}")
    print("-" * 50)
    
    # Create interviews for different people
    people = [
        {
            "email": "alice@company.com",
            "first_name": "Alice", 
            "last_name": "Johnson",
            "role": "Software Engineer"
        },
        {
            "email": "bob@company.com",
            "first_name": "Bob",
            "last_name": "Smith", 
            "role": "Product Manager"
        },
        {
            "email": "carol@company.com",
            "first_name": "Carol",
            "last_name": "Brown",
            "role": "Designer"
        }
    ]
    
    created_interviews = []
    
    for person in people:
        try:
            config = InterviewConfig(
                interview_flow_id=flow_id,
                interviewee_email_address=person['email'],
                interviewee_first_name=person['first_name'],
                interviewee_last_name=person['last_name']
            )
            
            interview = client.create_interview(config)
            interview_id = interview.get('interview_id')
            interview_link = interview.get('interview_link')
            
            print(f"✅ Created interview for {person['first_name']} {person['last_name']} ({person['role']})")
            print(f"   ID: {interview_id}")
            print(f"   Link: {interview_link}")
            
            created_interviews.append({
                'person': person,
                'interview_id': interview_id,
                'interview_link': interview_link
            })
            
        except Exception as e:
            print(f"❌ Failed to create interview for {person['first_name']}: {e}")
    
    return created_interviews


def check_interview_results(interviews):
    """Check the status and results of interviews"""
    client = RibbonClient()
    
    print(f"\n📊 Checking Interview Status and Results")
    print("-" * 50)
    
    for interview_data in interviews:
        person = interview_data['person']
        interview_id = interview_data['interview_id']
        
        try:
            # Get basic status
            status = client.get_interview_status(interview_id)
            
            print(f"\n👤 {person['first_name']} {person['last_name']} ({person['role']}):")
            print(f"   📋 Status: {status}")
            print(f"   🆔 Interview ID: {interview_id}")
            
            if status == "completed":
                # Get detailed results
                full_data = client.get_interview(interview_id)
                
                # Show transcript preview
                transcript = full_data.get('transcript', '')
                if transcript:
                    preview = transcript[:150] + "..." if len(transcript) > 150 else transcript
                    print(f"   📝 Transcript Preview: {preview}")
                    print(f"   📏 Transcript Length: {len(transcript)} characters")
                
                # Show audio URL
                audio_url = full_data.get('audio_url', '')
                if audio_url:
                    print(f"   🎵 Audio Recording: {audio_url}")
                
                # Show questions mapping
                questions_mapping = full_data.get('questions_to_transcript_mapping', [])
                print(f"   ❓ Questions Answered: {len(questions_mapping)}")
                
                if questions_mapping:
                    print(f"   ⏱️  Interview Duration: {questions_mapping[-1].get('end_timestamp', 0):.1f} seconds")
                
                # Show transcript with timestamps (first question as example)
                if questions_mapping:
                    first_q = questions_mapping[0]
                    print(f"   📄 First Question: '{first_q.get('script_question', '')}'")
                    print(f"      ⏰ Timestamp: {first_q.get('start_timestamp', 0):.1f}s - {first_q.get('end_timestamp', 0):.1f}s")
                
            else:
                print(f"   ⏳ Interview not yet completed")
                print(f"   🔗 Share this link: {interview_data['interview_link']}")
                
        except Exception as e:
            print(f"   ❌ Error checking interview: {e}")


def main():
    """Main demonstration with flow creation options"""
    print("🎯 Ribbon AI Interview Management Demo")
    print("=" * 60)
    
    # Ask user what they want to do
    print("\n🔧 Choose an option:")
    print("1. Create new interview flows")
    print("2. Use existing flows")
    print("3. Complete workflow (create + test)")
    print("4. Create custom flow")
    
    choice = input("\nEnter your choice (1-4) or press Enter for option 2: ").strip()
    
    if choice == "1":
        # Create sample flows
        print("\n🚀 Creating Sample Interview Flows...")
        created_flows = create_sample_interview_flows()
        
        if created_flows:
            print(f"\n✅ Successfully created {len(created_flows)} flows!")
            for flow in created_flows:
                print(f"   - {flow['title']} (ID: {flow['flow_id']})")
            
            # Use the first created flow for demonstration
            demo_flow = created_flows[0]
            print(f"\n🎯 Using newly created flow for demonstration: {demo_flow['title']}")
            
            # Create interviews with the new flow
            interviews = demonstrate_interview_management(demo_flow)
            if interviews:
                check_interview_results(interviews)
        else:
            print("\n❌ No flows were created. Falling back to existing flows...")
            choice = "2"  # Fall through to existing flows
    
    elif choice == "3":
        # Complete workflow
        print("\n🚀 Running Complete Workflow...")
        workflow_result = demonstrate_flow_creation_workflow()
        
        if workflow_result and workflow_result['simple_flow']:
            print(f"\n🎯 Continuing with created flow for full demonstration...")
            interviews = demonstrate_interview_management(workflow_result['simple_flow'])
            if interviews:
                check_interview_results(interviews)
        return
    
    elif choice == "4":
        # Create custom flow
        print("\n🎯 Creating Custom Flow...")
        print("Enter details for your custom interview flow:")
        
        org_name = input("Organization name: ").strip() or "My Company"
        title = input("Interview title: ").strip() or "Custom Interview"
        
        print("\nEnter questions (press Enter twice when done):")
        questions = []
        while True:
            question = input(f"Question {len(questions) + 1}: ").strip()
            if not question:
                if questions:  # If we have at least one question
                    break
                else:
                    print("Please enter at least one question.")
                    continue
            questions.append(question)
        
        interview_type = input("\nInterview type (recruitment/general) [general]: ").strip().lower()
        if interview_type not in ["recruitment", "general"]:
            interview_type = "general"
        
        # Create the custom flow
        custom_flow = create_custom_interview_flow(
            org_name=org_name,
            title=title,
            questions=questions,
            interview_type=interview_type
        )
        
        if custom_flow:
            # Test and demonstrate with the custom flow
            test_created_flow(custom_flow)
            interviews = demonstrate_interview_management(custom_flow)
            if interviews:
                check_interview_results(interviews)
        return
    
    # Default: Use existing flows (option 2 or fallback)
    if choice == "2" or choice == "":
        print("\n🔍 Looking for existing flows...")
        working_flows = list_existing_flows()
        
        if not working_flows:
            print("\n❌ No working flows found. Let's create some!")
            print("Creating sample flows...")
            created_flows = create_sample_interview_flows()
            
            if created_flows:
                working_flows = created_flows
                print(f"✅ Created and will use {len(working_flows)} new flows")
            else:
                print("\n❌ Could not create or find any flows. Please check:")
                print("   1. Your API key is valid")
                print("   2. Your API plan allows flow creation")
                print("   3. You haven't exceeded flow limits")
                return
        
        print(f"\n✅ Found {len(working_flows)} working flow(s)")
        
        # Use the first working flow for demonstration
        demo_flow = working_flows[0]
        print(f"\n🎯 Using flow {demo_flow['flow_id']} for demonstration")
        
        # Create multiple interviews
        interviews = demonstrate_interview_management(demo_flow)
        
        if not interviews:
            print("\n❌ No interviews were created successfully")
            return
        
        # Check results
        check_interview_results(interviews)
    
    # Final summary
    print(f"\n� Demo Complete!")
    print("-" * 30)
    print("💡 You can now:")
    print("   - Share interview links with participants")
    print("   - Monitor interviews using monitor_single_interview()")
    print("   - Create more flows with create_custom_interview_flow()")
    print("   - Retrieve results when interviews are completed")


def monitor_single_interview(interview_id: str, max_checks: int = 20, interval: int = 30):
    """Monitor a single interview until completion"""
    client = RibbonClient()
    
    print(f"🔄 Monitoring interview: {interview_id}")
    print(f"⏰ Checking every {interval} seconds (max {max_checks} checks)")
    
    for check in range(1, max_checks + 1):
        try:
            status = client.get_interview_status(interview_id)
            print(f"Check {check}/{max_checks}: Status = {status}")
            
            if status == "completed":
                print("🎉 Interview completed!")
                
                # Get and display results
                interview_data = client.get_interview(interview_id)
                transcript = interview_data.get('transcript', '')
                
                print(f"📝 Transcript ({len(transcript)} chars): {transcript[:200]}...")
                print(f"🎵 Audio: {interview_data.get('audio_url', 'N/A')}")
                
                return interview_data
            
            elif status == "incomplete":
                if check < max_checks:
                    print(f"⏳ Waiting {interval} seconds...")
                    time.sleep(interval)
                else:
                    print("⏰ Max checks reached. Interview still pending.")
            
            else:
                print(f"❓ Unknown status: {status}")
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
        
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            break
    
    return None


if __name__ == "__main__":
    main()
    
    # Example usage for creating specific flows:
    
    # To create a quick feedback flow:
    # feedback_flow = create_custom_interview_flow(
    #     org_name="Your Company",
    #     title="Product Feedback",
    #     questions=[
    #         "What do you like most about our product?",
    #         "What would you improve?",
    #         "How likely are you to recommend us?"
    #     ]
    # )
    
    # To create a technical interview:
    # tech_flow = create_custom_interview_flow(
    #     org_name="Tech Corp",
    #     title="Frontend Developer Interview", 
    #     questions=[
    #         "Explain your experience with React/Vue/Angular",
    #         "How do you optimize web application performance?",
    #         "Describe your CSS methodology and best practices"
    #     ],
    #     interview_type="recruitment"
    # )
    
    # To monitor a specific interview:
    # monitor_single_interview("your-interview-id-here")


# Quick utility functions for common use cases

def quick_feedback_flow(org_name: str, product_name: str = "our product"):
    """Create a quick customer feedback flow"""
    return create_custom_interview_flow(
        org_name=org_name,
        title=f"{product_name} Feedback Collection",
        questions=[
            f"How would you rate your overall experience with {product_name}?",
            f"What features of {product_name} do you find most valuable?",
            f"What challenges have you encountered while using {product_name}?",
            f"What improvements would you like to see in {product_name}?",
            f"How likely are you to recommend {product_name} to others?",
            "Any additional feedback or suggestions?"
        ],
        interview_type="general",
        additional_info=f"Customer feedback collection for {product_name}"
    )


def quick_onboarding_flow(org_name: str):
    """Create a quick employee onboarding feedback flow"""
    return create_custom_interview_flow(
        org_name=org_name,
        title="New Employee Onboarding Feedback",
        questions=[
            "How would you rate your onboarding experience so far?",
            "What aspects of onboarding were most helpful?",
            "What information or support was missing during onboarding?",
            "How well prepared do you feel for your new role?",
            "What would you improve about the onboarding process?",
            "Any other feedback about your first week?"
        ],
        interview_type="general",
        additional_info="Collecting feedback on employee onboarding experience"
    )


def quick_exit_interview_flow(org_name: str):
    """Create a quick exit interview flow"""
    return create_custom_interview_flow(
        org_name=org_name,
        title="Exit Interview",
        questions=[
            "What is your primary reason for leaving?",
            "How would you rate your overall experience working here?",
            "What did you enjoy most about your role?",
            "What would you change about your role or the company?",
            "How would you rate your relationship with your manager?",
            "Would you consider returning to work here in the future?",
            "Any additional feedback for the organization?"
        ],
        interview_type="general",
        additional_info="Exit interview to gather feedback from departing employees"
    )
