import asyncio
from backend.app.services.report_service import generate_report

async def main():
    topic = "Impact of AI on diagnostic accuracy and patient outcomes"
    
    # We will mock the output from the summarization service for testing
    summaries = [
        "Artificial intelligence (AI) is fundamentally transforming healthcare by significantly enhancing diagnostic accuracy. Its core capability lies in rapidly processing and analyzing immense volumes of medical data, allowing AI to identify subtle patterns that human practitioners might overlook, leading directly to earlier and more precise disease detection.",
        
        "The direct impact of AI-driven diagnostics on patient outcomes is profound. Earlier and more accurate diagnoses are critical for successful treatment, as evidenced by significantly higher survival rates for diseases like cancer when detected in their initial stages.",
        
        "However, implementing AI in clinical settings is not without challenges. Key issues include data privacy concerns, the potential for algorithmic bias if training data lacks diversity, and the need for seamless integration into existing hospital workflows. Overcoming these hurdles requires careful ethical oversight."
    ]
    
    print(f"Generating final research report on: '{topic}'...\n")
    print("This might take a few seconds as the LLM synthesizes the information...\n")
    
    report = await generate_report(topic, summaries)
    
    print("=" * 60)
    print("FINAL MARKDOWN REPORT")
    print("=" * 60)
    print(report)
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
