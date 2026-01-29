Q1. Why I Chose This Chunk Size ?

Answer : I have chosen Chunk Size = 500 characters and Overlap = 50 characters. 

The chunk size was chosen by balancing three competing factors:

1. Semantic Completeness :
    • Chunks below ~300 characters often lack enough context to answer meaningful   questions.
    • 500 characters usually contain a full paragraph or a complete idea.

2. Embedding Quality :
    • The embedding model (sentence-transformers/all-MiniLM-L6-v2) performs best when input text  represents a coherent semantic unit.
    • Larger chunks (>800 characters) tend to dilute meaning and reduce retrieval precision.

3. Retrieval Efficiency :
    • Smaller chunks increase the number of vectors, which increases retrieval time.
    • 500 characters keeps the FAISS index compact and fast.

A 50-character overlap ensures:
    • Important sentences at chunk boundaries are not split
    • Context continuity is preserved across chunks

This improves recall without significantly increasing index size.

----*----*----*----*----*----*----*----*----*----*----*----*----*----*----*----*-----

Q2. One Retrieval Failure Case I Observed ?

Answer : The Failure Case was --->
    
Query : “What are the limitations mentioned in the conclusion ?”
    
Observed Issue : The system retrieved chunks discussing general limitations but missed the actual conclusion section.

Root Cause :
    • FAISS similarity search is purely semantic, not structural.
    • The word “conclusion” was not semantically emphasized in embeddings.
    • Other sections discussed similar concepts (e.g., limitations, challenges), causing them to rank higher.

Possible Improvements :
    • Section-aware chunking (using headings)
    • Hybrid retrieval (keyword + vector search)
    • Increasing k during retrieval
    • Re-ranking retrieved chunks using a cross-encoder

----*----*----*----*----*----*----*----*----*----*----*----*----*----*----*----*-----

Q3. Metric that I Tracked ?

Answer : Metric [End-to-End Latency]

Definition : Time taken from user question submission to answer generation.

    Why Latency?
    • Directly impacts user experience
    • Includes retrieval + LLM inference
    • Easy to measure and interpret

Observed Values (Average) : 

Stage	                      |      Time
Vector Retrieval	      |    ~20–40 ms
OpenRouter LLM Response	      |    ~1.2–2.5 s
Total	                      |    ~1.3–2.6 s

Conclusion : Latency is dominated by LLM inference, not retrieval.The system meets acceptable response times for an applied RAG system.