# KGFactExplainer: Knowledge Graph-Based Fact Inclusion Explanation for Abstractive Summarization

This repository contains the implementation, data-processing scripts, evaluation code, and supporting resources for the paper:

> **Knowledge Graph-Based Fact Inclusion Explanation for Abstractive Summarization**

The project introduces **KGFactExplainer**, a post-hoc, source-grounded explanation framework for identifying and explaining why specific facts are included in an abstractive summary. The approach represents source documents as knowledge graphs and generates evidence paths connecting summary facts to information in the source document.

---

## Overview

Abstractive summarization systems can generate factually supported information while providing little insight into **how a particular summary fact is supported by the source document**.

KGFactExplainer addresses this problem by:

1. Extracting subject–predicate–object (SPO) triplets from the source document and generated summary.
2. Representing source information as a document-level knowledge graph.
3. Identifying evidence paths connecting summary facts to source information.
4. Classifying the level of source support for each summary fact.
5. Training a lightweight language model to generate evidence paths using knowledge-graph reasoning data.
6. Evaluating the generated explanations against reference evidence paths.

The framework categorizes fact inclusion into three confidence levels:

* **Direct Support (2):** The summary fact is directly supported by the source.
* **Inferential Support (1):** The summary fact can be supported through a multi-step inference over the source knowledge graph.
* **Unsupported (0):** No valid supporting evidence path can be established.

---
