const LEADERBOARD_DATA = {
  "cq2term": {
    "groups": [
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/awo/cq_to_terms_awo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/awo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/awo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/awo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/awo/cq_to_terms_awo.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/awo_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/awo_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "awo",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/awo/cq_to_terms_awo.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/awo_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/awo_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 100.0,
                "r": 100.0,
                "f1": 100.0,
                "tp": 7,
                "fp": 0,
                "fn": 0
              },
              "property": {
                "p": 100.0,
                "r": 100.0,
                "f1": 100.0,
                "tp": 1,
                "fp": 0,
                "fn": 0
              },
              "combined": {
                "p": 100.0,
                "r": 100.0,
                "f1": 100.0,
                "tp": 8,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 100.0,
                "mean": 100.0,
                "full": 100.0
              },
              "per_method_class": {
                "hard_match": {
                  "p": 85.71428571428571,
                  "r": 85.71428571428571,
                  "f1": 85.71428571428571,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 100.0,
                  "r": 100.0,
                  "f1": 100.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.5758387755102042,
              "agg_top3_property": 1.0
            },
            "status": null
          }
        ]
      },
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/odrl/cq_to_terms_odrl.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/odrl_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/odrl_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/odrl/cq_to_terms_odrl.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/odrl_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/odrl_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "odrl",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/odrl/cq_to_terms_odrl.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/odrl_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/odrl_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 41.37931034482759,
                "r": 92.3076923076923,
                "f1": 57.14285714285715,
                "tp": 12,
                "fp": 17,
                "fn": 1
              },
              "property": {
                "p": 45.45454545454545,
                "r": 38.46153846153847,
                "f1": 41.666666666666664,
                "tp": 10,
                "fp": 12,
                "fn": 16
              },
              "combined": {
                "p": 43.13725490196079,
                "r": 56.41025641025641,
                "f1": 48.88888888888889,
                "tp": 22,
                "fp": 29,
                "fn": 17
              },
              "cq": {
                "any": 57.89473684210526,
                "mean": 20.713684210526313,
                "full": 5.2631578947368425
              },
              "per_method_class": {
                "hard_match": {
                  "p": 31.03448275862069,
                  "r": 69.23076923076923,
                  "f1": 42.85714285714286,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 34.48275862068966,
                  "r": 76.92307692307693,
                  "f1": 47.61904761904761,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 31.03448275862069,
                  "r": 69.23076923076923,
                  "f1": 42.85714285714286,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 37.93103448275862,
                  "r": 84.61538461538461,
                  "f1": 52.38095238095239,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 34.48275862068966,
                  "r": 76.92307692307693,
                  "f1": 47.61904761904761,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 13.636363636363635,
                  "r": 11.538461538461538,
                  "f1": 12.499999999999996,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 40.909090909090914,
                  "r": 34.61538461538461,
                  "f1": 37.50000000000001,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 18.181818181818183,
                  "r": 15.384615384615385,
                  "f1": 16.666666666666668,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 40.909090909090914,
                  "r": 34.61538461538461,
                  "f1": 37.50000000000001,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 22.727272727272727,
                  "r": 19.230769230769234,
                  "f1": 20.833333333333332,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.45267400530503976,
              "agg_top3_property": 0.43739143356643356
            },
            "status": null
          }
        ]
      },
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/swo/cq_to_terms_swo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/swo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/swo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/swo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/swo/cq_to_terms_swo.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/swo_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/swo_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "swo",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/swo/cq_to_terms_swo.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/swo_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/swo_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 55.55555555555556,
                "r": 75.0,
                "f1": 63.829787234042556,
                "tp": 15,
                "fp": 12,
                "fn": 5
              },
              "property": {
                "p": 41.17647058823529,
                "r": 77.77777777777779,
                "f1": 53.84615384615385,
                "tp": 14,
                "fp": 20,
                "fn": 4
              },
              "combined": {
                "p": 47.540983606557376,
                "r": 76.31578947368422,
                "f1": 58.58585858585859,
                "tp": 29,
                "fp": 32,
                "fn": 9
              },
              "cq": {
                "any": 92.3076923076923,
                "mean": 44.61538461538463,
                "full": 7.6923076923076925
              },
              "per_method_class": {
                "hard_match": {
                  "p": 33.33333333333333,
                  "r": 45.0,
                  "f1": 38.297872340425535,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 51.85185185185185,
                  "r": 70.0,
                  "f1": 59.57446808510639,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 33.33333333333333,
                  "r": 45.0,
                  "f1": 38.297872340425535,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 55.55555555555556,
                  "r": 75.0,
                  "f1": 63.829787234042556,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 40.74074074074074,
                  "r": 55.00000000000001,
                  "f1": 46.808510638297875,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 8.823529411764707,
                  "r": 16.666666666666664,
                  "f1": 11.538461538461538,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 44.11764705882353,
                  "r": 83.33333333333334,
                  "f1": 57.6923076923077,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 11.76470588235294,
                  "r": 22.22222222222222,
                  "f1": 15.384615384615383,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 38.23529411764706,
                  "r": 72.22222222222221,
                  "f1": 49.999999999999986,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 17.647058823529413,
                  "r": 33.33333333333333,
                  "f1": 23.076923076923077,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.42457611111111127,
              "agg_top3_property": 0.4550468954248365
            },
            "status": null
          }
        ]
      },
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/vgo/cq_to_terms_vgo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/vgo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/vgo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/vgo/cq_to_terms_vgo.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/vgo_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/vgo_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "vgo",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/vgo/cq_to_terms_vgo.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/vgo_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/vgo_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 63.63636363636363,
                "r": 100.0,
                "f1": 77.77777777777779,
                "tp": 7,
                "fp": 4,
                "fn": 0
              },
              "property": {
                "p": 55.00000000000001,
                "r": 78.57142857142857,
                "f1": 64.70588235294117,
                "tp": 11,
                "fp": 9,
                "fn": 3
              },
              "combined": {
                "p": 58.06451612903226,
                "r": 85.71428571428571,
                "f1": 69.23076923076923,
                "tp": 18,
                "fp": 13,
                "fn": 3
              },
              "cq": {
                "any": 95.45454545454545,
                "mean": 69.69772727272729,
                "full": 40.90909090909091
              },
              "per_method_class": {
                "hard_match": {
                  "p": 54.54545454545454,
                  "r": 85.71428571428571,
                  "f1": 66.66666666666666,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 63.63636363636363,
                  "r": 100.0,
                  "f1": 77.77777777777779,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 54.54545454545454,
                  "r": 85.71428571428571,
                  "f1": 66.66666666666666,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 63.63636363636363,
                  "r": 100.0,
                  "f1": 77.77777777777779,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 63.63636363636363,
                  "r": 100.0,
                  "f1": 77.77777777777779,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 25.0,
                  "r": 35.714285714285715,
                  "f1": 29.411764705882348,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 50.0,
                  "r": 71.42857142857143,
                  "f1": 58.823529411764696,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 30.0,
                  "r": 42.857142857142854,
                  "f1": 35.29411764705882,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 55.00000000000001,
                  "r": 78.57142857142857,
                  "f1": 64.70588235294117,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 40.0,
                  "r": 57.14285714285714,
                  "f1": 47.05882352941176,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.5013558441558442,
              "agg_top3_property": 0.4797689285714287
            },
            "status": null
          }
        ]
      },
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/water/cq_to_terms_water.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/water_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/water_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/water/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/water/cq_to_terms_water.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/water_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/water_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/water/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "water",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/water/cq_to_terms_water.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/water_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/water/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/water_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 57.89473684210527,
                "r": 73.33333333333333,
                "f1": 64.70588235294117,
                "tp": 11,
                "fp": 8,
                "fn": 4
              },
              "property": {
                "p": 60.0,
                "r": 75.0,
                "f1": 66.66666666666666,
                "tp": 15,
                "fp": 10,
                "fn": 5
              },
              "combined": {
                "p": 59.09090909090909,
                "r": 74.28571428571429,
                "f1": 65.82278481012659,
                "tp": 26,
                "fp": 18,
                "fn": 9
              },
              "cq": {
                "any": 90.0,
                "mean": 53.6675,
                "full": 0.0
              },
              "per_method_class": {
                "hard_match": {
                  "p": 47.368421052631575,
                  "r": 60.0,
                  "f1": 52.94117647058824,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 57.89473684210527,
                  "r": 73.33333333333333,
                  "f1": 64.70588235294117,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 47.368421052631575,
                  "r": 60.0,
                  "f1": 52.94117647058824,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 63.1578947368421,
                  "r": 80.0,
                  "f1": 70.58823529411765,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 52.63157894736842,
                  "r": 66.66666666666666,
                  "f1": 58.82352941176471,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 28.000000000000004,
                  "r": 35.0,
                  "f1": 31.11111111111111,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 52.0,
                  "r": 65.0,
                  "f1": 57.777777777777786,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 32.0,
                  "r": 40.0,
                  "f1": 35.55555555555556,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 56.00000000000001,
                  "r": 70.0,
                  "f1": 62.22222222222222,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 40.0,
                  "r": 50.0,
                  "f1": 44.44444444444445,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.4739291228070176,
              "agg_top3_property": 0.4967685999999998
            },
            "status": null
          }
        ]
      },
      {
        "label": "cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/wine/cq_to_terms_wine.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/wine_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/wine_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/wine/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3",
        "config": {
          "cq_terms.cq_coverage_mode": "cq_local",
          "cq_terms.final_threshold": 0.6,
          "cq_terms.gold_cq_to_terms": "00_gold_standard/wine/cq_to_terms_wine.json",
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/wine_cq2terms_terms.json",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/wine_report.md",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/term_coverage.csv",
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.top_n": 3
        },
        "runs": [
          {
            "benchmark": "cq2term",
            "mode": null,
            "model": "pseudo_submission",
            "dataset": "wine",
            "config": {
              "cq_terms.gold_cq_to_terms": "00_gold_standard/wine/cq_to_terms_wine.json",
              "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/wine_cq2terms_terms.json",
              "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "cq_terms.top_n": 3,
              "cq_terms.final_threshold": 0.6,
              "cq_terms.semantic_threshold": 0.65,
              "cq_terms.lexical_threshold": 0.75,
              "cq_terms.hard_threshold": 1.0,
              "cq_terms.semantic_model": "embeddinggemma:latest",
              "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_trace.csv",
              "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_trace.csv",
              "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_best_matching.csv",
              "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_best_matching.csv",
              "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cq_coverage.csv",
              "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/term_coverage.csv",
              "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/eval_cq_terms_result.json",
              "cq_terms.save_report_md": "04_summary/pseudo_submission/wine_report.md",
              "cq_terms.cq_coverage_mode": "cq_local"
            },
            "term_recovery": {
              "class": {
                "p": 66.66666666666666,
                "r": 54.54545454545454,
                "f1": 60.0,
                "tp": 6,
                "fp": 3,
                "fn": 5
              },
              "property": {
                "p": 42.857142857142854,
                "r": 60.0,
                "f1": 50.0,
                "tp": 3,
                "fp": 4,
                "fn": 2
              },
              "combined": {
                "p": 56.25,
                "r": 56.25,
                "f1": 56.25,
                "tp": 9,
                "fp": 7,
                "fn": 7
              },
              "cq": {
                "any": 100.0,
                "mean": 50.0,
                "full": 0.0
              },
              "per_method_class": {
                "hard_match": {
                  "p": 55.55555555555556,
                  "r": 45.45454545454545,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 66.66666666666666,
                  "r": 54.54545454545454,
                  "f1": 60.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 55.55555555555556,
                  "r": 45.45454545454545,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 66.66666666666666,
                  "r": 54.54545454545454,
                  "f1": 60.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 55.55555555555556,
                  "r": 45.45454545454545,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "per_method_property": {
                "hard_match": {
                  "p": 28.57142857142857,
                  "r": 40.0,
                  "f1": 33.33333333333333,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "jaro_winkler": {
                  "p": 42.857142857142854,
                  "r": 60.0,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "levenshtein": {
                  "p": 28.57142857142857,
                  "r": 40.0,
                  "f1": 33.33333333333333,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "semantic": {
                  "p": 42.857142857142854,
                  "r": 60.0,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                },
                "sequence_match": {
                  "p": 42.857142857142854,
                  "r": 60.0,
                  "f1": 50.0,
                  "tp": 0,
                  "fp": 0,
                  "fn": 0
                }
              },
              "agg_top3_class": 0.5155515151515153,
              "agg_top3_property": 0.5235657142857145
            },
            "status": null
          }
        ]
      }
    ],
    "datasets": [
      "wine",
      "awo",
      "odrl",
      "water",
      "vgo",
      "swo"
    ],
    "models": [
      "pseudo_submission"
    ],
    "runs": [
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "swo",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/swo/cq_to_terms_swo.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/swo_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/swo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/swo_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 55.55555555555556,
            "r": 75.0,
            "f1": 63.829787234042556,
            "tp": 15,
            "fp": 12,
            "fn": 5
          },
          "property": {
            "p": 41.17647058823529,
            "r": 77.77777777777779,
            "f1": 53.84615384615385,
            "tp": 14,
            "fp": 20,
            "fn": 4
          },
          "combined": {
            "p": 47.540983606557376,
            "r": 76.31578947368422,
            "f1": 58.58585858585859,
            "tp": 29,
            "fp": 32,
            "fn": 9
          },
          "cq": {
            "any": 92.3076923076923,
            "mean": 44.61538461538463,
            "full": 7.6923076923076925
          },
          "per_method_class": {
            "hard_match": {
              "p": 33.33333333333333,
              "r": 45.0,
              "f1": 38.297872340425535,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 51.85185185185185,
              "r": 70.0,
              "f1": 59.57446808510639,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 33.33333333333333,
              "r": 45.0,
              "f1": 38.297872340425535,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 55.55555555555556,
              "r": 75.0,
              "f1": 63.829787234042556,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 40.74074074074074,
              "r": 55.00000000000001,
              "f1": 46.808510638297875,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 8.823529411764707,
              "r": 16.666666666666664,
              "f1": 11.538461538461538,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 44.11764705882353,
              "r": 83.33333333333334,
              "f1": 57.6923076923077,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 11.76470588235294,
              "r": 22.22222222222222,
              "f1": 15.384615384615383,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 38.23529411764706,
              "r": 72.22222222222221,
              "f1": 49.999999999999986,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 17.647058823529413,
              "r": 33.33333333333333,
              "f1": 23.076923076923077,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.42457611111111127,
          "agg_top3_property": 0.4550468954248365
        },
        "status": null
      },
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "odrl",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/odrl/cq_to_terms_odrl.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/odrl_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/odrl/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/odrl_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 41.37931034482759,
            "r": 92.3076923076923,
            "f1": 57.14285714285715,
            "tp": 12,
            "fp": 17,
            "fn": 1
          },
          "property": {
            "p": 45.45454545454545,
            "r": 38.46153846153847,
            "f1": 41.666666666666664,
            "tp": 10,
            "fp": 12,
            "fn": 16
          },
          "combined": {
            "p": 43.13725490196079,
            "r": 56.41025641025641,
            "f1": 48.88888888888889,
            "tp": 22,
            "fp": 29,
            "fn": 17
          },
          "cq": {
            "any": 57.89473684210526,
            "mean": 20.713684210526313,
            "full": 5.2631578947368425
          },
          "per_method_class": {
            "hard_match": {
              "p": 31.03448275862069,
              "r": 69.23076923076923,
              "f1": 42.85714285714286,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 34.48275862068966,
              "r": 76.92307692307693,
              "f1": 47.61904761904761,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 31.03448275862069,
              "r": 69.23076923076923,
              "f1": 42.85714285714286,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 37.93103448275862,
              "r": 84.61538461538461,
              "f1": 52.38095238095239,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 34.48275862068966,
              "r": 76.92307692307693,
              "f1": 47.61904761904761,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 13.636363636363635,
              "r": 11.538461538461538,
              "f1": 12.499999999999996,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 40.909090909090914,
              "r": 34.61538461538461,
              "f1": 37.50000000000001,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 18.181818181818183,
              "r": 15.384615384615385,
              "f1": 16.666666666666668,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 40.909090909090914,
              "r": 34.61538461538461,
              "f1": 37.50000000000001,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 22.727272727272727,
              "r": 19.230769230769234,
              "f1": 20.833333333333332,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.45267400530503976,
          "agg_top3_property": 0.43739143356643356
        },
        "status": null
      },
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "awo",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/awo/cq_to_terms_awo.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/awo_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/awo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/awo_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 100.0,
            "r": 100.0,
            "f1": 100.0,
            "tp": 7,
            "fp": 0,
            "fn": 0
          },
          "property": {
            "p": 100.0,
            "r": 100.0,
            "f1": 100.0,
            "tp": 1,
            "fp": 0,
            "fn": 0
          },
          "combined": {
            "p": 100.0,
            "r": 100.0,
            "f1": 100.0,
            "tp": 8,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 100.0,
            "mean": 100.0,
            "full": 100.0
          },
          "per_method_class": {
            "hard_match": {
              "p": 85.71428571428571,
              "r": 85.71428571428571,
              "f1": 85.71428571428571,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 100.0,
              "r": 100.0,
              "f1": 100.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.5758387755102042,
          "agg_top3_property": 1.0
        },
        "status": null
      },
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "water",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/water/cq_to_terms_water.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/water_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/water/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/water/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/water_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 57.89473684210527,
            "r": 73.33333333333333,
            "f1": 64.70588235294117,
            "tp": 11,
            "fp": 8,
            "fn": 4
          },
          "property": {
            "p": 60.0,
            "r": 75.0,
            "f1": 66.66666666666666,
            "tp": 15,
            "fp": 10,
            "fn": 5
          },
          "combined": {
            "p": 59.09090909090909,
            "r": 74.28571428571429,
            "f1": 65.82278481012659,
            "tp": 26,
            "fp": 18,
            "fn": 9
          },
          "cq": {
            "any": 90.0,
            "mean": 53.6675,
            "full": 0.0
          },
          "per_method_class": {
            "hard_match": {
              "p": 47.368421052631575,
              "r": 60.0,
              "f1": 52.94117647058824,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 57.89473684210527,
              "r": 73.33333333333333,
              "f1": 64.70588235294117,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 47.368421052631575,
              "r": 60.0,
              "f1": 52.94117647058824,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 63.1578947368421,
              "r": 80.0,
              "f1": 70.58823529411765,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 52.63157894736842,
              "r": 66.66666666666666,
              "f1": 58.82352941176471,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 28.000000000000004,
              "r": 35.0,
              "f1": 31.11111111111111,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 52.0,
              "r": 65.0,
              "f1": 57.777777777777786,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 32.0,
              "r": 40.0,
              "f1": 35.55555555555556,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 56.00000000000001,
              "r": 70.0,
              "f1": 62.22222222222222,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 40.0,
              "r": 50.0,
              "f1": 44.44444444444445,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.4739291228070176,
          "agg_top3_property": 0.4967685999999998
        },
        "status": null
      },
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "wine",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/wine/cq_to_terms_wine.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/wine_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/wine/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/wine_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 66.66666666666666,
            "r": 54.54545454545454,
            "f1": 60.0,
            "tp": 6,
            "fp": 3,
            "fn": 5
          },
          "property": {
            "p": 42.857142857142854,
            "r": 60.0,
            "f1": 50.0,
            "tp": 3,
            "fp": 4,
            "fn": 2
          },
          "combined": {
            "p": 56.25,
            "r": 56.25,
            "f1": 56.25,
            "tp": 9,
            "fp": 7,
            "fn": 7
          },
          "cq": {
            "any": 100.0,
            "mean": 50.0,
            "full": 0.0
          },
          "per_method_class": {
            "hard_match": {
              "p": 55.55555555555556,
              "r": 45.45454545454545,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 66.66666666666666,
              "r": 54.54545454545454,
              "f1": 60.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 55.55555555555556,
              "r": 45.45454545454545,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 66.66666666666666,
              "r": 54.54545454545454,
              "f1": 60.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 55.55555555555556,
              "r": 45.45454545454545,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 28.57142857142857,
              "r": 40.0,
              "f1": 33.33333333333333,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 42.857142857142854,
              "r": 60.0,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 28.57142857142857,
              "r": 40.0,
              "f1": 33.33333333333333,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 42.857142857142854,
              "r": 60.0,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 42.857142857142854,
              "r": 60.0,
              "f1": 50.0,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.5155515151515153,
          "agg_top3_property": 0.5235657142857145
        },
        "status": null
      },
      {
        "benchmark": "cq2term",
        "mode": null,
        "model": "pseudo_submission",
        "dataset": "vgo",
        "config": {
          "cq_terms.gold_cq_to_terms": "00_gold_standard/vgo/cq_to_terms_vgo.json",
          "cq_terms.pred_cq_to_terms": "01_predictions/pseudo_submission/terms/vgo_cq2terms_terms.json",
          "cq_terms.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "cq_terms.top_n": 3,
          "cq_terms.final_threshold": 0.6,
          "cq_terms.semantic_threshold": 0.65,
          "cq_terms.lexical_threshold": 0.75,
          "cq_terms.hard_threshold": 1.0,
          "cq_terms.semantic_model": "embeddinggemma:latest",
          "cq_terms.save_class_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_trace.csv",
          "cq_terms.save_property_alignment_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_trace.csv",
          "cq_terms.save_class_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_best_matching.csv",
          "cq_terms.save_property_best_matching_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_best_matching.csv",
          "cq_terms.save_cq_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cq_coverage.csv",
          "cq_terms.save_term_coverage_csv": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/term_coverage.csv",
          "cq_terms.save_result_json": "03_evaluation_results/pseudo_submission/vgo/06_cq_terms/eval_cq_terms_result.json",
          "cq_terms.save_report_md": "04_summary/pseudo_submission/vgo_report.md",
          "cq_terms.cq_coverage_mode": "cq_local"
        },
        "term_recovery": {
          "class": {
            "p": 63.63636363636363,
            "r": 100.0,
            "f1": 77.77777777777779,
            "tp": 7,
            "fp": 4,
            "fn": 0
          },
          "property": {
            "p": 55.00000000000001,
            "r": 78.57142857142857,
            "f1": 64.70588235294117,
            "tp": 11,
            "fp": 9,
            "fn": 3
          },
          "combined": {
            "p": 58.06451612903226,
            "r": 85.71428571428571,
            "f1": 69.23076923076923,
            "tp": 18,
            "fp": 13,
            "fn": 3
          },
          "cq": {
            "any": 95.45454545454545,
            "mean": 69.69772727272729,
            "full": 40.90909090909091
          },
          "per_method_class": {
            "hard_match": {
              "p": 54.54545454545454,
              "r": 85.71428571428571,
              "f1": 66.66666666666666,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 63.63636363636363,
              "r": 100.0,
              "f1": 77.77777777777779,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 54.54545454545454,
              "r": 85.71428571428571,
              "f1": 66.66666666666666,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 63.63636363636363,
              "r": 100.0,
              "f1": 77.77777777777779,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 63.63636363636363,
              "r": 100.0,
              "f1": 77.77777777777779,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "per_method_property": {
            "hard_match": {
              "p": 25.0,
              "r": 35.714285714285715,
              "f1": 29.411764705882348,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "jaro_winkler": {
              "p": 50.0,
              "r": 71.42857142857143,
              "f1": 58.823529411764696,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "levenshtein": {
              "p": 30.0,
              "r": 42.857142857142854,
              "f1": 35.29411764705882,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "semantic": {
              "p": 55.00000000000001,
              "r": 78.57142857142857,
              "f1": 64.70588235294117,
              "tp": 0,
              "fp": 0,
              "fn": 0
            },
            "sequence_match": {
              "p": 40.0,
              "r": 57.14285714285714,
              "f1": 47.05882352941176,
              "tp": 0,
              "fp": 0,
              "fn": 0
            }
          },
          "agg_top3_class": 0.5013558441558442,
          "agg_top3_property": 0.4797689285714287
        },
        "status": null
      }
    ]
  },
  "cq2onto": {
    "groups": [
      {
        "label": "axiom.literal_relax=False, axiom.no_layer2=False, axiom.threshold=0.6, concept.final_threshold=0.6, concept.hard_threshold=1.0, concept.lexical_threshold=0.8, concept.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, concept.model_id=embeddinggemma, concept.semantic_threshold=0.6, concept.top_n=3, property.final_threshold=0.7, property.hard_threshold=1.0, property.lexical_threshold=0.8, property.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, property.model_id=embeddinggemma, property.semantic_threshold=0.6, property.top_n=3, triple.literal_relax=False, triple.model_id=embeddinggemma, triple.threshold=0.6",
        "config": {
          "axiom.literal_relax": false,
          "axiom.no_layer2": false,
          "axiom.threshold": 0.6,
          "concept.final_threshold": 0.6,
          "concept.hard_threshold": 1.0,
          "concept.lexical_threshold": 0.8,
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.model_id": "embeddinggemma",
          "concept.semantic_threshold": 0.6,
          "concept.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.model_id": "embeddinggemma",
          "property.semantic_threshold": 0.6,
          "property.top_n": 3,
          "triple.literal_relax": false,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6
        },
        "runs": [
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "swo",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 55.55555555555556,
                  "r": 33.33333333333333,
                  "f1": 41.666666666666664,
                  "tp": 10,
                  "fp": 8,
                  "fn": 20
                },
                "agg_top3": 0.413936296296296,
                "per_method": {
                  "hard_match": {
                    "p": 11.11111111111111,
                    "r": 6.666666666666667,
                    "f1": 8.333333333333334,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 22.22222222222222,
                    "r": 13.333333333333334,
                    "f1": 16.666666666666668,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 16.666666666666664,
                    "r": 10.0,
                    "f1": 12.5,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 38.88888888888889,
                    "r": 23.333333333333332,
                    "f1": 29.166666666666668,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 72.22222222222221,
                    "r": 43.333333333333336,
                    "f1": 54.166666666666664,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 22.5,
                  "r": 39.130434782608695,
                  "f1": 28.57142857142857,
                  "tp": 9,
                  "fp": 31,
                  "fn": 14
                },
                "agg_top3": 0.47320541082164314,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": 0.0,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 2,
                "fn": 0
              },
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": null,
                "tp": 0,
                "fp": 2,
                "fn": 1
              }
            },
            "triple": {
              "ac": {
                "p": 5.56,
                "r": 16.669999999999998,
                "f1": 8.33,
                "tp": 1,
                "fp": 12,
                "fn": 0
              },
              "g": {
                "p": 1.25,
                "r": 5.56,
                "f1": 2.04,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 30.0,
                "r": 52.17,
                "f1": 38.1,
                "tp": 12,
                "fp": 28,
                "fn": 11
              }
            },
            "axiom": {
              "ac": {
                "p": 48.78048780487805,
                "r": 71.42857142857143,
                "f1": 57.971014492753625,
                "tp": 20,
                "fp": 21,
                "fn": 8
              },
              "g": {
                "p": 12.903225806451612,
                "r": 23.25581395348837,
                "f1": 16.597510373443985,
                "tp": 20,
                "fp": 135,
                "fn": 66
              },
              "cosine": {
                "p": 46.45161290322581,
                "r": 83.72093023255815,
                "f1": 59.75103734439834,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 71.42857142857143,
                "mean": 20.657999999999998,
                "full": 0.0
              }
            },
            "hierarchy": {
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 1,
                "fn": 8
              },
              "cq": {
                "any": 71.43,
                "mean": 20.66,
                "full": 0.0
              }
            },
            "status": null
          },
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "odrl",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 40.0,
                  "r": 66.66666666666666,
                  "f1": 49.99999999999999,
                  "tp": 10,
                  "fp": 15,
                  "fn": 5
                },
                "agg_top3": 0.45309653333333305,
                "per_method": {
                  "hard_match": {
                    "p": 28.000000000000004,
                    "r": 46.666666666666664,
                    "f1": 35.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 28.000000000000004,
                    "r": 46.666666666666664,
                    "f1": 35.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 28.000000000000004,
                    "r": 46.666666666666664,
                    "f1": 35.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 40.0,
                    "r": 66.66666666666666,
                    "f1": 50.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 48.0,
                    "r": 80.0,
                    "f1": 60.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 10.526315789473683,
                  "r": 7.142857142857142,
                  "f1": 8.510638297872342,
                  "tp": 2,
                  "fp": 17,
                  "fn": 26
                },
                "agg_top3": 0.4225404761904759,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "g": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            },
            "triple": {
              "ac": {
                "p": 50.0,
                "r": 100.0,
                "f1": 66.67,
                "tp": 2,
                "fp": 2,
                "fn": 0
              },
              "g": {
                "p": 5.26,
                "r": 6.0600000000000005,
                "f1": 5.63,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 57.89,
                "r": 39.290000000000006,
                "f1": 46.81,
                "tp": 11,
                "fp": 8,
                "fn": 17
              }
            },
            "axiom": {
              "ac": {
                "p": 9.523809523809524,
                "r": 18.181818181818183,
                "f1": 12.500000000000002,
                "tp": 2,
                "fp": 19,
                "fn": 9
              },
              "g": {
                "p": 1.9417475728155338,
                "r": 3.3333333333333335,
                "f1": 2.4539877300613493,
                "tp": 2,
                "fp": 101,
                "fn": 58
              },
              "cosine": {
                "p": 39.80582524271845,
                "r": 68.33333333333333,
                "f1": 50.306748466257666,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 16.666666666666668,
                "mean": 6.388888888888888,
                "full": 0.0
              }
            },
            "hierarchy": {
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 30,
                "fn": 13
              },
              "cq": {
                "any": 16.669999999999998,
                "mean": 6.39,
                "full": 0.0
              }
            },
            "status": null
          },
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "awo",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 100.0,
                  "r": 87.5,
                  "f1": 93.33333333333333,
                  "tp": 7,
                  "fp": 0,
                  "fn": 1
                },
                "agg_top3": 0.5789160714285717,
                "per_method": {
                  "hard_match": {
                    "p": 85.71428571428571,
                    "r": 75.0,
                    "f1": 80.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 100.0,
                    "r": 87.5,
                    "f1": 93.33333333333333,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 100.0,
                    "r": 87.5,
                    "f1": 93.33333333333333,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 100.0,
                    "r": 87.5,
                    "f1": 93.33333333333333,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 100.0,
                    "r": 87.5,
                    "f1": 93.33333333333333,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 33.33333333333333,
                  "r": 20.0,
                  "f1": 24.999999999999996,
                  "tp": 1,
                  "fp": 2,
                  "fn": 4
                },
                "agg_top3": 0.5466866666666667,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "g": {
                "p": null,
                "r": 0.0,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 4
              }
            },
            "triple": {
              "ac": {
                "p": 0.0,
                "r": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 2,
                "fn": 0
              },
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 66.67,
                "r": 40.0,
                "f1": 50.0,
                "tp": 2,
                "fp": 1,
                "fn": 3
              }
            },
            "axiom": {
              "ac": {
                "p": 22.22222222222222,
                "r": 30.76923076923077,
                "f1": 25.806451612903224,
                "tp": 4,
                "fp": 14,
                "fn": 9
              },
              "g": {
                "p": 16.666666666666664,
                "r": 16.0,
                "f1": 16.3265306122449,
                "tp": 4,
                "fp": 20,
                "fn": 21
              },
              "cosine": {
                "p": 62.5,
                "r": 60.0,
                "f1": 61.22448979591836,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 100.0,
                "mean": 32.57714285714286,
                "full": 0.0
              }
            },
            "hierarchy": {
              "g": {
                "p": 100.0,
                "r": 50.0,
                "f1": 66.67,
                "tp": 4,
                "fp": 0,
                "fn": 4
              },
              "cq": {
                "any": 100.0,
                "mean": 32.58,
                "full": 0.0
              }
            },
            "status": null
          },
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "water",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 66.66666666666666,
                  "r": 60.0,
                  "f1": 63.1578947368421,
                  "tp": 12,
                  "fp": 6,
                  "fn": 8
                },
                "agg_top3": 0.4574441666666666,
                "per_method": {
                  "hard_match": {
                    "p": 33.33333333333333,
                    "r": 30.0,
                    "f1": 31.57894736842105,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 38.88888888888889,
                    "r": 35.0,
                    "f1": 36.84210526315789,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 33.33333333333333,
                    "r": 30.0,
                    "f1": 31.57894736842105,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 55.55555555555556,
                    "r": 50.0,
                    "f1": 52.63157894736842,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 77.77777777777779,
                    "r": 70.0,
                    "f1": 73.68421052631578,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 40.0,
                  "r": 50.0,
                  "f1": 44.44444444444444,
                  "tp": 12,
                  "fp": 18,
                  "fn": 12
                },
                "agg_top3": 0.4716463483146064,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "g": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            },
            "triple": {
              "ac": {
                "p": 8.33,
                "r": 25.0,
                "f1": 12.5,
                "tp": 2,
                "fp": 16,
                "fn": 0
              },
              "g": {
                "p": 3.3300000000000005,
                "r": 11.110000000000001,
                "f1": 5.13,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 40.0,
                "r": 50.0,
                "f1": 44.440000000000005,
                "tp": 12,
                "fp": 18,
                "fn": 12
              }
            },
            "axiom": {
              "ac": {
                "p": 4.761904761904762,
                "r": 13.636363636363635,
                "f1": 7.058823529411765,
                "tp": 3,
                "fp": 60,
                "fn": 19
              },
              "g": {
                "p": 2.2058823529411766,
                "r": 6.976744186046512,
                "f1": 3.35195530726257,
                "tp": 3,
                "fp": 133,
                "fn": 40
              },
              "cosine": {
                "p": 27.941176470588236,
                "r": 88.37209302325581,
                "f1": 42.45810055865922,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 23.80952380952381,
                "mean": 4.86,
                "full": 0.0
              }
            },
            "hierarchy": {
              "g": {
                "p": 15.379999999999999,
                "r": 15.379999999999999,
                "f1": 15.379999999999999,
                "tp": 2,
                "fp": 11,
                "fn": 11
              },
              "cq": {
                "any": 23.810000000000002,
                "mean": 4.859999999999999,
                "full": 0.0
              }
            },
            "status": null
          },
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "wine",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 73.33333333333333,
                  "r": 64.70588235294117,
                  "f1": 68.75,
                  "tp": 11,
                  "fp": 4,
                  "fn": 6
                },
                "agg_top3": 0.49355137254901976,
                "per_method": {
                  "hard_match": {
                    "p": 20.0,
                    "r": 17.647058823529413,
                    "f1": 18.750000000000004,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 33.33333333333333,
                    "r": 29.411764705882355,
                    "f1": 31.25,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 20.0,
                    "r": 17.647058823529413,
                    "f1": 18.750000000000004,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 53.333333333333336,
                    "r": 47.05882352941176,
                    "f1": 50.0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 93.33333333333333,
                    "r": 82.35294117647058,
                    "f1": 87.49999999999999,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 33.33333333333333,
                  "r": 22.22222222222222,
                  "f1": 26.666666666666664,
                  "tp": 2,
                  "fp": 4,
                  "fn": 7
                },
                "agg_top3": 0.5075951219512196,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": null,
                "r": 0.0,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 1
              },
              "g": {
                "p": null,
                "r": 0.0,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 6
              }
            },
            "triple": {
              "ac": {
                "p": 25.0,
                "r": 25.0,
                "f1": 25.0,
                "tp": 1,
                "fp": 0,
                "fn": 0
              },
              "g": {
                "p": 8.33,
                "r": 6.67,
                "f1": 7.41,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 100.0,
                "r": 66.67,
                "f1": 80.0,
                "tp": 6,
                "fp": 0,
                "fn": 3
              }
            },
            "axiom": {
              "ac": {
                "p": 55.55555555555556,
                "r": 50.0,
                "f1": 52.63157894736842,
                "tp": 15,
                "fp": 12,
                "fn": 15
              },
              "g": {
                "p": 30.612244897959183,
                "r": 22.058823529411764,
                "f1": 25.641025641025646,
                "tp": 15,
                "fp": 34,
                "fn": 53
              },
              "cosine": {
                "p": 85.71428571428571,
                "r": 61.76470588235294,
                "f1": 71.7948717948718,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 100.0,
                "mean": 25.182000000000002,
                "full": 0.0
              }
            },
            "hierarchy": {
              "g": {
                "p": 11.110000000000001,
                "r": 8.7,
                "f1": 9.76,
                "tp": 2,
                "fp": 16,
                "fn": 21
              },
              "cq": {
                "any": 100.0,
                "mean": 25.180000000000003,
                "full": 0.0
              }
            },
            "status": null
          },
          {
            "benchmark": "cq2onto",
            "mode": "challenge",
            "model": "pseudo_submission",
            "dataset": "vgo",
            "config": {
              "concept.model_id": "embeddinggemma",
              "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "concept.top_n": 3,
              "concept.final_threshold": 0.6,
              "concept.semantic_threshold": 0.6,
              "concept.lexical_threshold": 0.8,
              "concept.hard_threshold": 1.0,
              "property.model_id": "embeddinggemma",
              "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
              "property.top_n": 3,
              "property.final_threshold": 0.7,
              "property.hard_threshold": 1.0,
              "property.lexical_threshold": 0.8,
              "property.semantic_threshold": 0.6,
              "triple.model_id": "embeddinggemma",
              "triple.threshold": 0.6,
              "triple.literal_relax": false,
              "axiom.threshold": 0.6,
              "axiom.no_layer2": false,
              "axiom.literal_relax": false
            },
            "term_recovery": {
              "class": {
                "aggregated": {
                  "p": 57.14285714285714,
                  "r": 33.33333333333333,
                  "f1": 42.10526315789473,
                  "tp": 8,
                  "fp": 6,
                  "fn": 16
                },
                "agg_top3": 0.4356625,
                "per_method": {
                  "hard_match": {
                    "p": 35.714285714285715,
                    "r": 20.833333333333336,
                    "f1": 26.31578947368421,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": 50.0,
                    "r": 29.166666666666668,
                    "f1": 36.84210526315789,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": 35.714285714285715,
                    "r": 20.833333333333336,
                    "f1": 26.31578947368421,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": 57.14285714285714,
                    "r": 33.33333333333333,
                    "f1": 42.10526315789474,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": 64.28571428571429,
                    "r": 37.5,
                    "f1": 47.36842105263159,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              },
              "property": {
                "aggregated": {
                  "p": 32.35294117647059,
                  "r": 39.285714285714285,
                  "f1": 35.483870967741936,
                  "tp": 11,
                  "fp": 23,
                  "fn": 17
                },
                "agg_top3": 0.4759783870967745,
                "per_method": {
                  "hard_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "sequence_match": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "levenshtein": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "jaro_winkler": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  },
                  "semantic": {
                    "p": null,
                    "r": null,
                    "f1": null,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0
                  }
                }
              }
            },
            "property_chars": {
              "ac": {
                "p": 0.0,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 3,
                "fn": 0
              },
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": null,
                "tp": 0,
                "fp": 3,
                "fn": 1
              }
            },
            "triple": {
              "ac": {
                "p": 54.55,
                "r": 54.55,
                "f1": 54.55,
                "tp": 12,
                "fp": 0,
                "fn": 0
              },
              "g": {
                "p": 17.65,
                "r": 22.64,
                "f1": 19.830000000000002,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cosine": {
                "p": 58.81999999999999,
                "r": 71.43,
                "f1": 64.52,
                "tp": 20,
                "fp": 14,
                "fn": 8
              }
            },
            "axiom": {
              "ac": {
                "p": 26.666666666666668,
                "r": 48.0,
                "f1": 34.285714285714285,
                "tp": 12,
                "fp": 33,
                "fn": 13
              },
              "g": {
                "p": 8.633093525179856,
                "r": 15.584415584415584,
                "f1": 11.11111111111111,
                "tp": 12,
                "fp": 127,
                "fn": 65
              },
              "cosine": {
                "p": 36.69064748201439,
                "r": 66.23376623376623,
                "f1": 47.22222222222222,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "cq": {
                "any": 38.70967741935484,
                "mean": 18.28258064516129,
                "full": 6.451612903225806
              }
            },
            "hierarchy": {
              "g": {
                "p": 0.0,
                "r": 0.0,
                "f1": 0.0,
                "tp": 0,
                "fp": 1,
                "fn": 12
              },
              "cq": {
                "any": 38.71,
                "mean": 18.279999999999998,
                "full": 6.45
              }
            },
            "status": null
          }
        ]
      }
    ],
    "datasets": [
      "wine",
      "awo",
      "odrl",
      "water",
      "vgo",
      "swo"
    ],
    "modes": [
      "challenge"
    ],
    "models": [
      "pseudo_submission"
    ],
    "runs": [
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "swo",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 55.55555555555556,
              "r": 33.33333333333333,
              "f1": 41.666666666666664,
              "tp": 10,
              "fp": 8,
              "fn": 20
            },
            "agg_top3": 0.413936296296296,
            "per_method": {
              "hard_match": {
                "p": 11.11111111111111,
                "r": 6.666666666666667,
                "f1": 8.333333333333334,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 22.22222222222222,
                "r": 13.333333333333334,
                "f1": 16.666666666666668,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 16.666666666666664,
                "r": 10.0,
                "f1": 12.5,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 38.88888888888889,
                "r": 23.333333333333332,
                "f1": 29.166666666666668,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 72.22222222222221,
                "r": 43.333333333333336,
                "f1": 54.166666666666664,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 22.5,
              "r": 39.130434782608695,
              "f1": 28.57142857142857,
              "tp": 9,
              "fp": 31,
              "fn": 14
            },
            "agg_top3": 0.47320541082164314,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": 0.0,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 2,
            "fn": 0
          },
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": null,
            "tp": 0,
            "fp": 2,
            "fn": 1
          }
        },
        "triple": {
          "ac": {
            "p": 5.56,
            "r": 16.669999999999998,
            "f1": 8.33,
            "tp": 1,
            "fp": 12,
            "fn": 0
          },
          "g": {
            "p": 1.25,
            "r": 5.56,
            "f1": 2.04,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 30.0,
            "r": 52.17,
            "f1": 38.1,
            "tp": 12,
            "fp": 28,
            "fn": 11
          }
        },
        "axiom": {
          "ac": {
            "p": 48.78048780487805,
            "r": 71.42857142857143,
            "f1": 57.971014492753625,
            "tp": 20,
            "fp": 21,
            "fn": 8
          },
          "g": {
            "p": 12.903225806451612,
            "r": 23.25581395348837,
            "f1": 16.597510373443985,
            "tp": 20,
            "fp": 135,
            "fn": 66
          },
          "cosine": {
            "p": 46.45161290322581,
            "r": 83.72093023255815,
            "f1": 59.75103734439834,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 71.42857142857143,
            "mean": 20.657999999999998,
            "full": 0.0
          }
        },
        "hierarchy": {
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 1,
            "fn": 8
          },
          "cq": {
            "any": 71.43,
            "mean": 20.66,
            "full": 0.0
          }
        },
        "status": null
      },
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "odrl",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 40.0,
              "r": 66.66666666666666,
              "f1": 49.99999999999999,
              "tp": 10,
              "fp": 15,
              "fn": 5
            },
            "agg_top3": 0.45309653333333305,
            "per_method": {
              "hard_match": {
                "p": 28.000000000000004,
                "r": 46.666666666666664,
                "f1": 35.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 28.000000000000004,
                "r": 46.666666666666664,
                "f1": 35.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 28.000000000000004,
                "r": 46.666666666666664,
                "f1": 35.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 40.0,
                "r": 66.66666666666666,
                "f1": 50.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 48.0,
                "r": 80.0,
                "f1": 60.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 10.526315789473683,
              "r": 7.142857142857142,
              "f1": 8.510638297872342,
              "tp": 2,
              "fp": 17,
              "fn": 26
            },
            "agg_top3": 0.4225404761904759,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": null,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "g": {
            "p": null,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 0
          }
        },
        "triple": {
          "ac": {
            "p": 50.0,
            "r": 100.0,
            "f1": 66.67,
            "tp": 2,
            "fp": 2,
            "fn": 0
          },
          "g": {
            "p": 5.26,
            "r": 6.0600000000000005,
            "f1": 5.63,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 57.89,
            "r": 39.290000000000006,
            "f1": 46.81,
            "tp": 11,
            "fp": 8,
            "fn": 17
          }
        },
        "axiom": {
          "ac": {
            "p": 9.523809523809524,
            "r": 18.181818181818183,
            "f1": 12.500000000000002,
            "tp": 2,
            "fp": 19,
            "fn": 9
          },
          "g": {
            "p": 1.9417475728155338,
            "r": 3.3333333333333335,
            "f1": 2.4539877300613493,
            "tp": 2,
            "fp": 101,
            "fn": 58
          },
          "cosine": {
            "p": 39.80582524271845,
            "r": 68.33333333333333,
            "f1": 50.306748466257666,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 16.666666666666668,
            "mean": 6.388888888888888,
            "full": 0.0
          }
        },
        "hierarchy": {
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 30,
            "fn": 13
          },
          "cq": {
            "any": 16.669999999999998,
            "mean": 6.39,
            "full": 0.0
          }
        },
        "status": null
      },
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "awo",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 100.0,
              "r": 87.5,
              "f1": 93.33333333333333,
              "tp": 7,
              "fp": 0,
              "fn": 1
            },
            "agg_top3": 0.5789160714285717,
            "per_method": {
              "hard_match": {
                "p": 85.71428571428571,
                "r": 75.0,
                "f1": 80.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 100.0,
                "r": 87.5,
                "f1": 93.33333333333333,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 100.0,
                "r": 87.5,
                "f1": 93.33333333333333,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 100.0,
                "r": 87.5,
                "f1": 93.33333333333333,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 100.0,
                "r": 87.5,
                "f1": 93.33333333333333,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 33.33333333333333,
              "r": 20.0,
              "f1": 24.999999999999996,
              "tp": 1,
              "fp": 2,
              "fn": 4
            },
            "agg_top3": 0.5466866666666667,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": null,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "g": {
            "p": null,
            "r": 0.0,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 4
          }
        },
        "triple": {
          "ac": {
            "p": 0.0,
            "r": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 2,
            "fn": 0
          },
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 66.67,
            "r": 40.0,
            "f1": 50.0,
            "tp": 2,
            "fp": 1,
            "fn": 3
          }
        },
        "axiom": {
          "ac": {
            "p": 22.22222222222222,
            "r": 30.76923076923077,
            "f1": 25.806451612903224,
            "tp": 4,
            "fp": 14,
            "fn": 9
          },
          "g": {
            "p": 16.666666666666664,
            "r": 16.0,
            "f1": 16.3265306122449,
            "tp": 4,
            "fp": 20,
            "fn": 21
          },
          "cosine": {
            "p": 62.5,
            "r": 60.0,
            "f1": 61.22448979591836,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 100.0,
            "mean": 32.57714285714286,
            "full": 0.0
          }
        },
        "hierarchy": {
          "g": {
            "p": 100.0,
            "r": 50.0,
            "f1": 66.67,
            "tp": 4,
            "fp": 0,
            "fn": 4
          },
          "cq": {
            "any": 100.0,
            "mean": 32.58,
            "full": 0.0
          }
        },
        "status": null
      },
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "water",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 66.66666666666666,
              "r": 60.0,
              "f1": 63.1578947368421,
              "tp": 12,
              "fp": 6,
              "fn": 8
            },
            "agg_top3": 0.4574441666666666,
            "per_method": {
              "hard_match": {
                "p": 33.33333333333333,
                "r": 30.0,
                "f1": 31.57894736842105,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 38.88888888888889,
                "r": 35.0,
                "f1": 36.84210526315789,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 33.33333333333333,
                "r": 30.0,
                "f1": 31.57894736842105,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 55.55555555555556,
                "r": 50.0,
                "f1": 52.63157894736842,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 77.77777777777779,
                "r": 70.0,
                "f1": 73.68421052631578,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 40.0,
              "r": 50.0,
              "f1": 44.44444444444444,
              "tp": 12,
              "fp": 18,
              "fn": 12
            },
            "agg_top3": 0.4716463483146064,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": null,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "g": {
            "p": null,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 0
          }
        },
        "triple": {
          "ac": {
            "p": 8.33,
            "r": 25.0,
            "f1": 12.5,
            "tp": 2,
            "fp": 16,
            "fn": 0
          },
          "g": {
            "p": 3.3300000000000005,
            "r": 11.110000000000001,
            "f1": 5.13,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 40.0,
            "r": 50.0,
            "f1": 44.440000000000005,
            "tp": 12,
            "fp": 18,
            "fn": 12
          }
        },
        "axiom": {
          "ac": {
            "p": 4.761904761904762,
            "r": 13.636363636363635,
            "f1": 7.058823529411765,
            "tp": 3,
            "fp": 60,
            "fn": 19
          },
          "g": {
            "p": 2.2058823529411766,
            "r": 6.976744186046512,
            "f1": 3.35195530726257,
            "tp": 3,
            "fp": 133,
            "fn": 40
          },
          "cosine": {
            "p": 27.941176470588236,
            "r": 88.37209302325581,
            "f1": 42.45810055865922,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 23.80952380952381,
            "mean": 4.86,
            "full": 0.0
          }
        },
        "hierarchy": {
          "g": {
            "p": 15.379999999999999,
            "r": 15.379999999999999,
            "f1": 15.379999999999999,
            "tp": 2,
            "fp": 11,
            "fn": 11
          },
          "cq": {
            "any": 23.810000000000002,
            "mean": 4.859999999999999,
            "full": 0.0
          }
        },
        "status": null
      },
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "wine",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 73.33333333333333,
              "r": 64.70588235294117,
              "f1": 68.75,
              "tp": 11,
              "fp": 4,
              "fn": 6
            },
            "agg_top3": 0.49355137254901976,
            "per_method": {
              "hard_match": {
                "p": 20.0,
                "r": 17.647058823529413,
                "f1": 18.750000000000004,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 33.33333333333333,
                "r": 29.411764705882355,
                "f1": 31.25,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 20.0,
                "r": 17.647058823529413,
                "f1": 18.750000000000004,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 53.333333333333336,
                "r": 47.05882352941176,
                "f1": 50.0,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 93.33333333333333,
                "r": 82.35294117647058,
                "f1": 87.49999999999999,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 33.33333333333333,
              "r": 22.22222222222222,
              "f1": 26.666666666666664,
              "tp": 2,
              "fp": 4,
              "fn": 7
            },
            "agg_top3": 0.5075951219512196,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": null,
            "r": 0.0,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 1
          },
          "g": {
            "p": null,
            "r": 0.0,
            "f1": null,
            "tp": 0,
            "fp": 0,
            "fn": 6
          }
        },
        "triple": {
          "ac": {
            "p": 25.0,
            "r": 25.0,
            "f1": 25.0,
            "tp": 1,
            "fp": 0,
            "fn": 0
          },
          "g": {
            "p": 8.33,
            "r": 6.67,
            "f1": 7.41,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 100.0,
            "r": 66.67,
            "f1": 80.0,
            "tp": 6,
            "fp": 0,
            "fn": 3
          }
        },
        "axiom": {
          "ac": {
            "p": 55.55555555555556,
            "r": 50.0,
            "f1": 52.63157894736842,
            "tp": 15,
            "fp": 12,
            "fn": 15
          },
          "g": {
            "p": 30.612244897959183,
            "r": 22.058823529411764,
            "f1": 25.641025641025646,
            "tp": 15,
            "fp": 34,
            "fn": 53
          },
          "cosine": {
            "p": 85.71428571428571,
            "r": 61.76470588235294,
            "f1": 71.7948717948718,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 100.0,
            "mean": 25.182000000000002,
            "full": 0.0
          }
        },
        "hierarchy": {
          "g": {
            "p": 11.110000000000001,
            "r": 8.7,
            "f1": 9.76,
            "tp": 2,
            "fp": 16,
            "fn": 21
          },
          "cq": {
            "any": 100.0,
            "mean": 25.180000000000003,
            "full": 0.0
          }
        },
        "status": null
      },
      {
        "benchmark": "cq2onto",
        "mode": "challenge",
        "model": "pseudo_submission",
        "dataset": "vgo",
        "config": {
          "concept.model_id": "embeddinggemma",
          "concept.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "concept.top_n": 3,
          "concept.final_threshold": 0.6,
          "concept.semantic_threshold": 0.6,
          "concept.lexical_threshold": 0.8,
          "concept.hard_threshold": 1.0,
          "property.model_id": "embeddinggemma",
          "property.methods": "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
          "property.top_n": 3,
          "property.final_threshold": 0.7,
          "property.hard_threshold": 1.0,
          "property.lexical_threshold": 0.8,
          "property.semantic_threshold": 0.6,
          "triple.model_id": "embeddinggemma",
          "triple.threshold": 0.6,
          "triple.literal_relax": false,
          "axiom.threshold": 0.6,
          "axiom.no_layer2": false,
          "axiom.literal_relax": false
        },
        "term_recovery": {
          "class": {
            "aggregated": {
              "p": 57.14285714285714,
              "r": 33.33333333333333,
              "f1": 42.10526315789473,
              "tp": 8,
              "fp": 6,
              "fn": 16
            },
            "agg_top3": 0.4356625,
            "per_method": {
              "hard_match": {
                "p": 35.714285714285715,
                "r": 20.833333333333336,
                "f1": 26.31578947368421,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": 50.0,
                "r": 29.166666666666668,
                "f1": 36.84210526315789,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": 35.714285714285715,
                "r": 20.833333333333336,
                "f1": 26.31578947368421,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": 57.14285714285714,
                "r": 33.33333333333333,
                "f1": 42.10526315789474,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": 64.28571428571429,
                "r": 37.5,
                "f1": 47.36842105263159,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          },
          "property": {
            "aggregated": {
              "p": 32.35294117647059,
              "r": 39.285714285714285,
              "f1": 35.483870967741936,
              "tp": 11,
              "fp": 23,
              "fn": 17
            },
            "agg_top3": 0.4759783870967745,
            "per_method": {
              "hard_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "sequence_match": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "levenshtein": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "jaro_winkler": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              },
              "semantic": {
                "p": null,
                "r": null,
                "f1": null,
                "tp": 0,
                "fp": 0,
                "fn": 0
              }
            }
          }
        },
        "property_chars": {
          "ac": {
            "p": 0.0,
            "r": null,
            "f1": null,
            "tp": 0,
            "fp": 3,
            "fn": 0
          },
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": null,
            "tp": 0,
            "fp": 3,
            "fn": 1
          }
        },
        "triple": {
          "ac": {
            "p": 54.55,
            "r": 54.55,
            "f1": 54.55,
            "tp": 12,
            "fp": 0,
            "fn": 0
          },
          "g": {
            "p": 17.65,
            "r": 22.64,
            "f1": 19.830000000000002,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cosine": {
            "p": 58.81999999999999,
            "r": 71.43,
            "f1": 64.52,
            "tp": 20,
            "fp": 14,
            "fn": 8
          }
        },
        "axiom": {
          "ac": {
            "p": 26.666666666666668,
            "r": 48.0,
            "f1": 34.285714285714285,
            "tp": 12,
            "fp": 33,
            "fn": 13
          },
          "g": {
            "p": 8.633093525179856,
            "r": 15.584415584415584,
            "f1": 11.11111111111111,
            "tp": 12,
            "fp": 127,
            "fn": 65
          },
          "cosine": {
            "p": 36.69064748201439,
            "r": 66.23376623376623,
            "f1": 47.22222222222222,
            "tp": 0,
            "fp": 0,
            "fn": 0
          },
          "cq": {
            "any": 38.70967741935484,
            "mean": 18.28258064516129,
            "full": 6.451612903225806
          }
        },
        "hierarchy": {
          "g": {
            "p": 0.0,
            "r": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 1,
            "fn": 12
          },
          "cq": {
            "any": 38.71,
            "mean": 18.279999999999998,
            "full": 6.45
          }
        },
        "status": null
      }
    ]
  },
  "methods": [
    "hard_match",
    "sequence_match",
    "levenshtein",
    "jaro_winkler",
    "semantic"
  ]
};
