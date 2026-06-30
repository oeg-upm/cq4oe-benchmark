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
    "groups": [],
    "datasets": [],
    "modes": [],
    "models": [],
    "runs": []
  },
  "methods": [
    "hard_match",
    "sequence_match",
    "levenshtein",
    "jaro_winkler",
    "semantic"
  ]
};
