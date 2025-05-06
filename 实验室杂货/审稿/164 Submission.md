# 164 Submission

1. Summary of the Paper *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
    500 characters left 

    This paper proposes a novel gaze estimation framework based on binocular visible-light cameras, using a hybrid approach that combines geometric modeling and machine learning. The authors introduce a PPAMR2U-Net for iris segmentation trained on synthetic UnityEyes data and employ MediaPipe and Bayesian Ridge Regression to map eye features to 3D gaze vectors. The method shows promising performance with reduced calibration and improved accuracy over Gazepointer.

2. Novelty and Originality: *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
     High 

3. Technical Quality and Correctness

*   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
 Good
4. Significance and Impact *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
     Significant 
5. Clarity and Presentation *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
     Acceptable 
6. Relevance to ICANN Topics *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
    Highly Relevant 
7. Confidential Comments to Program Committee *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
    8000 characters left 
8. Review (Comments to the Authors) *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
    8000 characters left 
    1. In the Experiments section, the authors compared the performance of four machine learning models and concluded that BR performed the best, but they did not provide a detailed explanation of the underlying reasons.
    2. The MPIIGaze dataset is cited but its core characteristics are not introduced in the text. It is recommended to add a paragraph describing the key features of this dataset in the paper.
    3. While the paper provides detailed descriptions of the three sub-modules (iris segmentation network, feature extraction, and gaze modeling), it lacks a unified pipeline or flowchart to illustrate the input/output relationships and connectivity between these stages.
    4. The authors placed the experiments of PPAMR2U-Net in the Methodology section, which makes the paper's structure somewhat confusing.
    5. The paper uses UnityEyes to synthesize a virtual dataset for testing PPAMR2U-Net, but does not report this net's performance on real-world scene datasets. While the article mentions the difficulty in acquiring real-world scene datasets, small-sample testing could still have been conducted.
    6. The paper fails to report any result of ablation studies.
9. Overall Recommendation *   (visible to other reviewers, visible to meta-reviewers, visible to senior meta-reviewers) 
    Weak Accept 