# 50 Submission

1. How confident are you in your evaluation of this paper? *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    Confidence 

2. Importance/Relevance *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    Of sufficient interest 

3. Novelty/Originality *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    original 

4. Technical Correctness *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    sounds Correct 

5. Experimental Validation *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    sufficient

6. Overall evaluation of this paper *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    accept 

7. How would you rank this paper in terms of award quality?   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    not awrad quality 

8. Did you use AI tools to assist in the evaluation of the manuscript during the review process? If not, please answer 'No'. If yes, kindly specify which areas (e.g., AI-content and plagiarism detection, summarization, evaluation) were supported by AI tools. *

    No

9. Additional comments to author(s): *   (visible to authors after notification, visible to other reviewers, visible to meta-reviewers) 

    The paper proposes a decomposition-driven two-stage unfolding network (DTUANet) for compression artifact removal. Overall, the paper is clearly written, the method is reasonable and technically sound, and the experiments are sufficient with comprehensive comparisons and ablations. However, it has the following limitations:

    1. There are some undefined abbreviations in the paper, such as "LSS" mentioned in Section 3.1, which is not formally defined.
    2. The visualized figures in the paper are presented in grayscale, which may cause confusion since the method is designed for color (RGB) images, as stated in Section 3.1. It is recommended that the authors use color visualizations to better demonstrate the effectiveness.
    3. The authors did not provide any analysis of the model’s inference time or computational complexity.
    4. The paper does not include comparisons with recent Transformer-based image restoration methods, which have shown strong performance in artifact removal and other image restoration tasks.
    5. The description of the proximal operator in the paper is mostly implementation-driven and lacks a clear mathematical definition. For readers who are not familiar with deep unfolding frameworks, this may cause confusion. 