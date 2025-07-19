"""
Working Example with Existing Flows

This example demonstrates how to:
1. Work with existing interview flows 
2. Create interviews
3. Retrieve interview results

Since the API plan has reached the flow creation limit, we'll use existing flows.
"""

from ribbon_client import RibbonClient, InterviewConfig
import time


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
    """Main demonstration"""
    print("🎯 Ribbon AI Interview Management Demo")
    print("=" * 60)
    
    # Step 1: Find working flows
    working_flows = list_existing_flows()
    
    if not working_flows:
        print("\n❌ No working flows found. You may need to:")
        print("   1. Create new interview flows if your API plan allows")
        print("   2. Use flow IDs from flows created with this account")
        print("   3. Check your API key permissions")
        return
    
    print(f"\n✅ Found {len(working_flows)} working flow(s)")
    
    # Step 2: Use the first working flow for demonstration
    demo_flow = working_flows[0]
    print(f"\n🎯 Using flow {demo_flow['flow_id']} for demonstration")
    
    # Step 3: Create multiple interviews
    interviews = demonstrate_interview_management(demo_flow)
    
    if not interviews:
        print("\n❌ No interviews were created successfully")
        return
    
    # Step 4: Check results
    check_interview_results(interviews)
    
    # Step 5: Summary and next steps
    print(f"\n📈 Demo Summary")
    print("-" * 30)
    print(f"✅ Working flows found: {len(working_flows)}")
    print(f"✅ Interviews created: {len(interviews)}")
    
    completed = 0
    for interview_data in interviews:
        try:
            client = RibbonClient()
            status = client.get_interview_status(interview_data['interview_id'])
            if status == "completed":
                completed += 1
        except:
            pass
    
    print(f"📊 Completed interviews: {completed}")
    print(f"⏳ Pending interviews: {len(interviews) - completed}")
    
    if len(interviews) - completed > 0:
        print(f"\n💡 Next Steps:")
        print(f"   1. Share interview links with participants")
        print(f"   2. Wait for participants to complete interviews")
        print(f"   3. Run this script again to see results")
        print(f"   4. Use the monitor_single_interview() function for real-time tracking")
    
    # Show monitoring command
    if interviews:
        sample = interviews[0]
        print(f"\n🔄 To monitor a specific interview:")
        print(f"   monitor_single_interview('{sample['interview_id']}')")


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
    
    # To monitor a specific interview, uncomment and replace with actual ID:
    # monitor_single_interview("your-interview-id-here")
