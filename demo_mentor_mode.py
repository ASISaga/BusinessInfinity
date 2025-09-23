#!/usr/bin/env python3
"""
Mentor Mode Demo Script for Business Infinity

This script demonstrates the key functionality of the integrated mentor mode.
"""

import asyncio
import sys
import os

# Add paths for imports
sys.path.append('.')
sys.path.append('./core')

from mentor_mode import MentorMode

async def demo_mentor_mode():
    """Demonstrate mentor mode functionality"""
    
    print("🚀 Business Infinity - Mentor Mode Demo")
    print("=" * 50)
    
    # Initialize mentor mode
    print("\n1. Initializing Mentor Mode...")
    mentor = MentorMode()
    await mentor.initialize()
    print("✓ Mentor Mode initialized successfully")
    
    # List available agents
    print("\n2. Loading Available Agents...")
    agents = await mentor.list_agents_with_lora()
    print(f"✓ Found {len(agents)} business agents:")
    
    for agent in agents:
        capabilities = ", ".join(agent["capabilities"])
        print(f"   • {agent['name']} ({agent['id']}) - v{agent['loraVersion']}")
        print(f"     Capabilities: {capabilities}")
        print(f"     Status: {agent['status']}")
    
    # Demonstrate chat functionality
    print("\n3. Testing Agent Chat (Sandboxed Environment)...")
    test_scenarios = [
        ("ceo", "What should our strategic priorities be for Q1?"),
        ("cfo", "Analyze the ROI of our current marketing spend"),
        ("cto", "What emerging technologies should we evaluate?")
    ]
    
    for agent_id, question in test_scenarios:
        print(f"\n   🗨️  Testing {agent_id.upper()} with: '{question}'")
        response = await mentor.chat_with_agent(agent_id, question)
        
        # Extract just the response part for cleaner output
        if "Response: " in response:
            clean_response = response.split("Response: ", 1)[1][:150] + "..."
        else:
            clean_response = response[:150] + "..."
            
        print(f"   💬 Response: {clean_response}")
    
    # Demonstrate training functionality  
    print("\n4. Testing Fine-Tuning Job Management...")
    training_scenarios = [
        ("ceo", "leadership_scenarios_v2"),
        ("cfo", "financial_analysis_v3")
    ]
    
    training_jobs = []
    for agent_id, dataset_id in training_scenarios:
        print(f"   🔧 Starting training job for {agent_id.upper()} with dataset: {dataset_id}")
        job = await mentor.start_fine_tune_job(agent_id, dataset_id)
        training_jobs.append(job["jobId"])
        print(f"   ✓ Job created: {job['jobId']}")
        print(f"   📊 Status: {job['status']} | Started: {job['startTime']}")
    
    # Wait a moment for jobs to progress
    print("\n   ⏳ Waiting for training jobs to progress...")
    await asyncio.sleep(3)
    
    # Check training logs
    print("\n5. Retrieving Training Logs...")
    for job_id in training_jobs[:1]:  # Just check first job to avoid spam
        logs = await mentor.get_training_logs(job_id)
        print(f"   📋 Logs for job {job_id}:")
        for log in logs[-3:]:  # Show last 3 log entries
            print(f"      {log}")
    
    # Demonstrate deployment simulation
    print("\n6. Testing Adapter Deployment...")
    deployment = await mentor.deploy_adapter("ceo", "v1.1.0")
    print(f"   🚢 Deployment Result:")
    print(f"      Agent: {deployment['agentId']}")
    print(f"      Version: {deployment['version']}")
    print(f"      Deployed At: {deployment['deployedAt']}")
    print(f"      Rollback Available: {deployment['rollbackAvailable']}")
    
    print("\n" + "=" * 50)
    print("✅ Mentor Mode Demo Complete!")
    print("\n📖 Next Steps:")
    print("   • Access Web UI: Navigate to /mentor/ui endpoint")
    print("   • Install VS Code Extension: Use files in /mentor directory") 
    print("   • Configure Environment: Set MENTOR_MODE_ENABLED=true")
    print("   • Add Training Data: Provide datasets for fine-tuning")

if __name__ == "__main__":
    try:
        asyncio.run(demo_mentor_mode())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)