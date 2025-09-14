# CARE v1.1.0 — Reviewer Quick Start (ملخص للمراجعين)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17113211.svg)](https://doi.org/10.5281/zenodo.17113211)

**TL;DR**  
In SCARCITY (60 agents), CARE achieves **Efficiency ≥ 0.96** and **Jain ≥ 0.85** (targets: 0.80 / 0.70) with fast convergence.  
في سيناريو الندرة (60 عميل)، يحقق CARE الكفاءة ≥ 0.96 وعدالة Jain ≥ 0.85 مع تقارب سريع.

---

## 1) What to review (ماذا تُقيّم؟)
- **Objectives:** Efficiency ≥ **0.80**, Fairness (Jain) ≥ **0.70**  
- **Artifacts:** figures + metrics + logs + checksum  
- **Docs:** docs/FIGMAP.md ، docs/EVIDENCE_MATRIX.csv

---

## 2) Zero-setup check (بدون إعداد)
1) نزّل من صفحة الإصدار v1.1.0:  
   CARE-FULL_20250913_160316.zip + CARE-FULL_20250913_160316.zip.sha256.txt
2) تحقّق من سلامة الملف (طابِق قيمة SHA256):
   
    shasum -a 256 CARE-FULL_20250913_160316.zip

    Get-FileHash .\CARE-FULL_20250913_160316.zip -Algorithm SHA256

3) افتح الصور الأساسية (S1..S4 + T1):
   - CARE_figure1_convergence_v1.1.0.png  → S1 Convergence  
   - CARE_figure2_satisfaction_v1.1.0.png → S2 Satisfaction  
   - CARE_figure3_combined_metrics_v1.1.0.png → S3 Combined  
   - CARE_figure4_success_zones_v1.1.0.png → S4 Success  
   - CARE_table1_final_results_v1.1.0.png → T1 Final table

> هذه الخطوة تكفي لإثبات النتائج بدون تشغيل الكود.

---

## 3) Minimal reproduce (تشغيل مختصر)
**Requirements:** Python ≥ 3.10

    pip install -r requirements.txt

    python scripts/run_experiment.py --scenario scarcity --agents 60 --episodes 100 --seed 33 --out results/CARE_v1.1.0_full

(انظر FIGMAP لتوليد الأشكال/الجداول.)

---

## 4) Figure → Message (ملخص سريع)
| ID | ملف الأثر (artifact)                            | الرسالة |
|----|-------------------------------------------------|---------|
| S1 | CARE_figure1_convergence_v1.1.0.png            | الكفاءة/العدالة تصل الأهداف؛ تقارب سريع |
| S2 | CARE_figure2_satisfaction_v1.1.0.png           | الرضا متذبذب وليس هدف التحسين |
| S3 | CARE_figure3_combined_metrics_v1.1.0.png       | اتجاه ↑ للكفاءة/العدالة مقابل رضا أقل |
| S4 | CARE_figure4_success_zones_v1.1.0.png          | داخل منطقة النجاح (≥0.80, ≥0.70) |
| T1 | CARE_table1_final_results_v1.1.0.png           | ملخص القيم النهائية ومتوسط آخر 10 |

التفاصيل: docs/FIGMAP.md و docs/EVIDENCE_MATRIX.csv

---

## 5) Cite / ترخيص
- DOI: https://doi.org/10.5281/zenodo.17113211  
- Code: MIT (LICENSE)  
- Content: CC BY 4.0 (LICENSE-CONTENT.txt)


