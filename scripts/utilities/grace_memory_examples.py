"""
Grace Memory Integration Examples
Demonstrates how Grace can use her memory system in various scenarios
"""

import asyncio
from backend.grace_memory_agent import get_grace_memory_agent
from backend.ingestion_pipeline import get_ingestion_pipeline
from backend.content_intelligence import get_content_intelligence


async def example_1_save_research():
    """
    Example 1: Grace saves research findings
    
    Use case: Grace reads a paper and saves key findings
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Grace Saves Research")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    
    result = await grace.save_research(
        title="Neural Architecture Search Findings",
        content="""
        # Neural Architecture Search - Key Findings
        
        ## Summary
        After analyzing 50+ papers on NAS, key insights:
        
        1. **Search Space Design** is critical
           - Cell-based search spaces more efficient
           - Direct encoding often too large
           
        2. **Search Strategy** impacts results
           - Evolution strategies: robust but slow
           - Gradient-based: fast but local optima risk
           - RL-based: good balance
           
        3. **Performance Estimation** bottleneck
           - Weight sharing reduces cost 10-100x
           - Early stopping critical for efficiency
           
        ## Recommendations
        - Start with DARTS for gradient-based NAS
        - Use weight sharing for large search spaces
        - Implement early stopping with correlation > 0.8
        
        ## Next Steps
        - Implement DARTS variant for Grace
        - Test on small datasets first
        - Compare with hand-designed architectures
        """,
        domain="ml",
        tags=["neural-architecture-search", "AutoML", "deep-learning", "optimization"],
        auto_sync=True
    )
    
    if result.get("success"):
        print(f"✓ Research saved to: {result['path']}")
        print(f"✓ Auto-synced to Memory Fusion: {result['synced']}")
        print(f"✓ File size: {result['size']} bytes")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result


async def example_2_detect_pattern():
    """
    Example 2: Grace detects pattern and saves insight
    
    Use case: After 100 user interactions, Grace notices a trend
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Grace Detects Pattern")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    
    # Grace observes that users ask similar questions
    pattern_insight = """
    PATTERN DETECTED: Embedding Optimization Questions
    
    After analyzing 100 user conversations, 67% of questions about embeddings
    fall into 3 categories:
    
    1. Chunk Size (34 questions)
       - Optimal size for different content types
       - Trade-offs between granularity and context
       
    2. Model Selection (22 questions)
       - Which embedding model to use
       - Cost vs. quality considerations
       
    3. Indexing Strategy (11 questions)
       - Vector database choice
       - Index optimization
       
    RECOMMENDATION:
    Create pre-canned responses for these topics.
    Build training examples focused on these areas.
    Add FAQ section to documentation.
    """
    
    result = await grace.save_insight(
        insight=pattern_insight,
        category_type="patterns",
        confidence=0.89,
        auto_sync=True
    )
    
    if result.get("success"):
        print(f"✓ Pattern insight saved to: {result['path']}")
        print(f"✓ Confidence: 0.89")
        print(f"✓ Auto-synced to Memory Fusion")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    return result


async def example_3_organize_uploads():
    """
    Example 3: Grace organizes uploaded files
    
    Use case: User uploads files to wrong location, Grace fixes it
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Grace Organizes Files")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    
    # Simulate user uploaded files to "uploads/" folder
    files_to_organize = [
        ("uploads/machine_learning_guide.pdf", "documentation", "guides"),
        ("uploads/train_model.py", "code", "python"),
        ("uploads/embeddings_dataset.json", "learning", "training_data"),
    ]
    
    for file_path, category, subcategory in files_to_organize:
        print(f"\nOrganizing: {file_path}")
        
        result = await grace.organize_file(
            file_path=file_path,
            suggested_category=category,
            suggested_subcategory=subcategory,
            auto_move=True
        )
        
        print(f"  ✓ Suggested: {category}/{subcategory}")
        print(f"  ✓ New path: {result['new_path']}")
        print(f"  ✓ Confidence: {result['confidence']}")
    
    print("\n✓ All files organized by Grace!")


async def example_4_learning_pipeline():
    """
    Example 4: Complete learning pipeline
    
    Use case: User uploads document, Grace processes it end-to-end
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Learning Pipeline")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    intelligence = await get_content_intelligence()
    pipeline_engine = await get_ingestion_pipeline()
    
    # Step 1: User uploads document
    print("\n1. Document uploaded: ai_textbook_chapter3.txt")
    document_content = """
    Chapter 3: Neural Network Optimization
    
    Gradient descent is the foundation of neural network training.
    Key concepts include learning rate, momentum, and batch size.
    Modern optimizers like Adam combine advantages of multiple approaches.
    """
    
    # Step 2: Grace analyzes quality
    print("\n2. Grace analyzes content quality")
    analysis = await intelligence.analyze_file(
        "ai_textbook_chapter3.txt",
        document_content
    )
    print(f"   ✓ Quality score: {analysis['quality_score']}/100")
    print(f"   ✓ Suggested tags: {', '.join(analysis['tags_suggested'][:5])}")
    print(f"   ✓ Domain: {analysis['domain_suggested']}")
    
    # Step 3: Grace organizes
    print("\n3. Grace organizes to appropriate category")
    result = await grace.organize_file(
        file_path="ai_textbook_chapter3.txt",
        suggested_category="learning",
        suggested_subcategory="training_data",
        auto_move=True
    )
    print(f"   ✓ Moved to: {result['new_path']}")
    
    # Step 4: Grace saves summary
    print("\n4. Grace generates summary")
    result = await grace.save_research(
        title="AI Textbook Ch3 Summary",
        content="Key concepts: gradient descent, learning rate, Adam optimizer",
        domain="ml",
        tags=["neural-networks", "optimization", "textbook"],
        auto_sync=False
    )
    print(f"   ✓ Summary saved to: {result['path']}")
    
    # Step 5: Start ingestion pipeline
    print("\n5. Starting ingestion pipeline")
    job_id = await pipeline_engine.start_pipeline(
        "text_to_embeddings",
        result['path']
    )
    print(f"   ✓ Pipeline started: {job_id}")
    
    # Step 6: Monitor progress
    print("\n6. Monitoring pipeline progress...")
    for i in range(5):
        await asyncio.sleep(1)
        job = pipeline_engine.get_job_status(job_id)
        if job:
            print(f"   Progress: {job['progress']}% - Stage: {job['status']}")
            if job['status'] == 'complete':
                break
    
    print("\n✓ Complete learning pipeline executed!")


async def example_5_contradiction_detection():
    """
    Example 5: Grace detects contradictions
    
    Use case: Grace finds conflicting information across files
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Contradiction Detection")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    
    # Grace detected contradiction between two sources
    contradiction = """
    CONTRADICTION DETECTED
    
    Source A: research/papers/paper_123.pdf (dated 2024-01-15)
    Claims: "Optimal chunk size for embeddings is 256 tokens"
    Context: Based on experiments with 1,000 documents
    
    Source B: research/notes/experiment_log_456.md (dated 2024-10-20)
    Claims: "Best results achieved with 512-token chunks"
    Context: Based on experiments with 10,000 documents
    
    ANALYSIS:
    - Source B is newer and has 10x more data
    - Source B likely more reliable
    - May indicate field has evolved
    
    RECOMMENDATION:
    1. Run A/B test with both chunk sizes
    2. Update documentation to reflect newer findings
    3. Mark paper_123.pdf metadata as "potentially outdated"
    
    CONFIDENCE: 0.87
    SEVERITY: Medium (affects embedding quality)
    """
    
    result = await grace.save_insight(
        insight=contradiction,
        category_type="contradictions",
        confidence=0.87,
        auto_sync=True
    )
    
    if result.get("success"):
        print(f"✓ Contradiction flagged and saved")
        print(f"✓ Path: {result['path']}")
        print(f"✓ Will alert user to review")
        print(f"✓ Synced to Memory Fusion for cross-kernel awareness")
    
    return result


async def example_6_training_data_prep():
    """
    Example 6: Grace prepares training dataset
    
    Use case: Grace collects and formats data for model training
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Training Data Preparation")
    print("="*60)
    
    grace = await get_grace_memory_agent()
    
    # Grace prepares Q&A dataset from conversations
    training_dataset = {
        "dataset_name": "user_qa_embeddings_v2",
        "created_at": "2024-11-12T20:30:00Z",
        "total_examples": 500,
        "format": "question_answer_pairs",
        "examples": [
            {
                "question": "How do I optimize embeddings?",
                "answer": "Three key strategies: 1) Choose optimal chunk size (512 tokens)...",
                "metadata": {"topic": "embeddings", "difficulty": "intermediate"}
            },
            # ... 499 more examples
        ],
        "metadata": {
            "source": "user_conversations",
            "topics": ["embeddings", "optimization", "neural-networks"],
            "quality_score": 88,
            "reviewed": True
        }
    }
    
    result = await grace.save_training_data(
        dataset_name="user_qa_embeddings_v2",
        data=training_dataset,
        data_type="embeddings",
        auto_sync=True
    )
    
    if result.get("success"):
        print(f"✓ Training dataset saved to: {result['path']}")
        print(f"✓ Contains 500 examples")
        print(f"✓ Ready for ML pipeline ingestion")
        print(f"✓ Synced to Memory Fusion")
    
    return result


async def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print(" " * 15 + "GRACE MEMORY INTEGRATION EXAMPLES")
    print("="*70)
    
    examples = [
        ("Research Management", example_1_save_research),
        ("Pattern Detection", example_2_detect_pattern),
        ("File Organization", example_3_organize_uploads),
        ("Learning Pipeline", example_4_learning_pipeline),
        ("Contradiction Detection", example_5_contradiction_detection),
        ("Training Data Prep", example_6_training_data_prep),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
            await asyncio.sleep(0.5)  # Brief pause between examples
        except Exception as e:
            print(f"\n✗ Example '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETE")
    print("="*70)
    print("\nGrace's memory system is fully operational!")
    print("Check grace_training/ folder to see created files.")
    print("\n" + "="*70)


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())
