# 0925-BSPC-D-25-07691_reviewer

This paper proposes a multi-scale EEG pipeline for schizophrenia screening: empirical wavelet transform splits signals into canonical rhythms; wavelet scattering extracts translation-stable features; an LSTM performs classification. The method is evaluated on two public datasets (adult and pediatric EEG) and reports high accuracies (~99.1% and ~98.8% at best). A MATLAB standalone app is provided for end-to-end inference. Overall, it is sufficiently innovative and experimental, but there are the following areas for improvement.

1. The manuscript reports an 80/20 split of signal features for training and testing, but it is not specified whether the split is performed at the epoch level or at the subject level.
2. It is suggested to show some reader-friendly “failure cases” so that the reader can understand the bound of the proposed method.
3. The authors failed to explain the reason for the consistently lower performance on Dataset B at the early scales (1–3).
4. The manuscript excludes frequencies above 60 Hz but provides no empirical justification.
5. Section 7.3 states that Dataset B is ‘smaller’ than Dataset A. Please revise this claim: B includes more subjects but offers less data per subject (shorter recordings, lower sampling rate), resulting in fewer usable epochs. Clarify this explicitly. otherwise it may cause misunderstanding. 
6. The authors didn't state the runtime assumptions or the time complexity of their method.
7. The authors should provide sufficient information in the caption of each figure to make it self-explanatory. 

