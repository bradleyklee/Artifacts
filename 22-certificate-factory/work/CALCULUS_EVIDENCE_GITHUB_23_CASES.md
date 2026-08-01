---
title: "Calculus Certificates for 23 Hanna-Family Sequences"
artifact_type: "human-readable mathematical evidence report"
schema_version: "1.0"
generated_date: "2026-07-30"
case_count: 23
scope: "A120588–A120607, A244594, A244627, A244856"
case_state: "ANALYTIC_COMPLETE"
arithmetic: "exact"
numerical_fitting: false
generator: "src/generate_github_calculus_report.py"
exhaustive_companion: "work/FULL_CALCULUS_EVIDENCE_23_CASES.md"
---

# Calculus certificates for 23 Hanna-family sequences

This report gives the mathematical evidence behind the completion claim
without duplicating the multi-megabyte internal derivation traces. The
exhaustive report remains available for forensic review.

## Standard notation and method

The algebraic generating function is $A(x)$ and its normalized shifted
series is $T(x)$. The local inverse is written $x=\rho(u)$ with
$u=T(x)$. Lagrange inversion gives

$$
a_n=\frac{c}{2\pi i\,n}\oint_\gamma\frac{du}{\rho(u)^n},
\qquad n\ge 1.
$$

Hermite reduction separates each shifted integrand into an exact derivative
and a finite-dimensional remainder. The exact matrices $G,U,V,J$ encode
the reduction and $X$ collects the remainder vectors. A kernel vector gives

$$
\sum_r P_r(n)a_{n+r}=0.
$$

The rational function $R(n,u)$ is the telescoping certificate: its
$u$-derivative equals the recurrence combination of integrands. Hence the
contour integral vanishes. Substituting the Euler operator
$\theta=x\,d/dx$ translates the recurrence into a scalar linear ODE.

For descendants, differentiation introduces numerator powers, so the
numerator-aware direct-$x$ reduction is used. A120589 requires an extra
shift because its seed fills the full remainder space. A244856 has both
an attached order-4 certificate and an independent order-5 cross-check;
minimality is not claimed.

## Coverage summary

| Evidence | Coverage |
|---|---:|
| Typogeometric models | 23/23 |
| Explicit small-set enumeration | 23/23 |
| Contour representations | 23/23 |
| Exact matrix reductions | 23/23 |
| Polynomial recurrences | 23/23 |
| Rational telescoping certificates | 23/23 |
| Scalar linear ODEs | 23/23 |
| Stored exact coefficients | 552/552 |
| Recorded checks passing | 46/46 |

## A120588

### Defining data

```json
{
  "b": 1,
  "c": 2,
  "equation": "3*A(x)=2+1*x+A(x)^2",
  "linear_coefficient_d": "1",
  "q": 2,
  "r": 3,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 1
  },
  "classification": "literal_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+1*T^2",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "3": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)"
    ],
    "2": [
      "root[0](Delta_2[0](l,l))"
    ],
    "3": [
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-1*u^1",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-1*u^1)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=1",
    "shape": [
      4,
      4
    ]
  },
  "expected_shift_count_for_first_nullvector": 2,
  "integrand": "(1)/(n*(-u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 1,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `data/matrices.json`

```json
{
  "bases": {
    "G_codomain_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3"
    ],
    "G_domain_basis": [
      "a_0",
      "a_1",
      "b_0",
      "b_1"
    ],
    "X_columns": [
      "shift r=0",
      "shift r=1"
    ],
    "X_rows": [
      "coefficient of u^0"
    ],
    "coefficient_order": "ascending powers of u",
    "polynomial_space_basis": [
      "1",
      "u^1"
    ]
  },
  "canonical_source": "data/matrices.json",
  "full_entries_location": "data/matrices.json",
  "matrix_shapes": {
    "G": [
      4,
      4
    ],
    "G_inverse": [
      4,
      4
    ],
    "J": [
      2,
      2
    ],
    "U": [
      2,
      2
    ],
    "V": [
      2,
      2
    ],
    "X": [
      1,
      2
    ],
    "X_full": [
      2,
      2
    ],
    "embedding_E": [
      4,
      2
    ]
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "4*n/(n + 1) - 2/(n + 1)"
        ]
      ],
      "shape": [
        1,
        2
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "4*n/(n + 1) - 2/(n + 1)"
        ],
        [
          "0",
          "0"
        ]
      ],
      "shape": [
        2,
        2
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `data/recurrence.json`

```json
{
  "legacy_top_level": [
    "-4*n + 2",
    "n + 1"
  ],
  "recurrence": {
    "coefficients": [
      "-4*n + 2",
      "n + 1"
    ],
    "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
    "order": 1,
    "valid_from_n": 1
  },
  "status": "verified"
}
```

### Rational telescoping certificate

Canonical source: `data/certificate.json`

```json
{
  "denominator_base": "-u**2 + u",
  "denominator_power": 0,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "2*u - 1",
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "3*x",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 19,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 20,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 21,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 22,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "2*x",
      "-4*x**2 + x"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 1
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-4*theta + 2",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      23
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        23
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    1,
    2,
    5,
    14
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    1,
    2,
    5,
    14,
    42,
    132,
    429,
    1430,
    4862,
    16796,
    58786,
    208012,
    742900,
    2674440,
    9694845,
    35357670,
    129644790,
    477638700,
    1767263190,
    6564120420,
    24466267020,
    91482563640
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120589

### Defining data

```json
{
  "observable": "A_parent(x)^2",
  "parent": "A120588",
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "observable power as ordered forest",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "classification": "colored_unweighted",
  "component": "tree_model",
  "model": "ordered forest of 2 parent A120588 typogeometries",
  "parent_branch_multiplicities": {
    "Delta_2": 1
  },
  "status": "verified",
  "top_constructor": "Delta_2 with all 2 positions occupied"
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    },
    "2": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "3": {
      "enumerated": 6,
      "pass": true,
      "published_term": 6
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "Delta_2F(false,root[0](l))",
      "Delta_2F(root[0](l),false)"
    ],
    "2": [
      "Delta_2F(false,root[0](Delta_2[0](l,l)))",
      "Delta_2F(root[0](l),root[0](l))",
      "Delta_2F(root[0](Delta_2[0](l,l)),false)"
    ],
    "3": [
      "Delta_2F(false,root[0](Delta_2[0](l,Delta_2[0](l,l))))",
      "Delta_2F(false,root[0](Delta_2[0](Delta_2[0](l,l),l)))",
      "Delta_2F(root[0](l),root[0](Delta_2[0](l,l)))",
      "Delta_2F(root[0](Delta_2[0](l,l)),root[0](l))",
      "Delta_2F(root[0](Delta_2[0](l,Delta_2[0](l,l))),false)",
      "Delta_2F(root[0](Delta_2[0](Delta_2[0](l,l),l)),false)"
    ]
  },
  "encoding": "ordered 2-forest; false is the unit parent object",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-1*u^1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "formula": "[x^n]A(x)^2=(2*1)/(2*pi*i*n)*integral_gamma (1+(1)*u)^1 du/(u^n*D(u)^n)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "invertibility_witness": "resultant(rho,rho')=1",
    "shape": [
      4,
      4
    ]
  },
  "expected_shift_count_for_first_nullvector": 2,
  "integrand": "(2)*(u + 1)/(n*(-u**2 + u)^n)",
  "kernel_class": "polynomial_power_with_fixed_seed",
  "q3_algorithm_relation": "identical G/U/V and pole lowering; initialize shift 0 with the coefficient vector of the fixed seed instead of e_0",
  "remainder_dimension": 1,
  "required_change": "accept a fixed numerator seed vector and propagate it through every shifted column",
  "seed_degree": 1,
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/matrices",
  "matrix_shapes": {},
  "remainder_matrices": {},
  "statistics": {
    "G_shape": [
      4,
      4
    ],
    "X_shape": [
      2,
      3
    ],
    "certificate_numerator_degree_n": 1,
    "certificate_numerator_degree_u": 2,
    "certificate_parameter_denominator": "n*u + n + u + 1",
    "denominator_degree": 2,
    "leading_zero_coefficients": 1,
    "nullity": 1,
    "rank": 2,
    "recurrence_order": 2,
    "remainder_dimension": 2,
    "shift_columns": 3
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/recurrence`

```json
[
  "0",
  "-4*n - 2",
  "n + 2"
]
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/certificate`

```json
{
  "N": "2*n*u**2/(n*u + n + u + 1) + n*u/(n*u + n + u + 1) - n/(n*u + n + u + 1) + u**2/(n*u + n + u + 1) - u/(n*u + n + u + 1)",
  "denominator_base": "-u**2 + u",
  "denominator_power": 1
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/ode`

```json
{
  "boundary_polynomial": "2*x**2 + 4*x",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 19,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 20,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "2*x",
      "-4*x**2 + x"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 1
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "0",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-4*theta + 2",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      22
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        22
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    2,
    3,
    6,
    15,
    42
  ],
  "status": "verified",
  "terms": [
    1,
    2,
    3,
    6,
    15,
    42,
    126,
    396,
    1287,
    4290,
    14586,
    50388,
    176358,
    624036,
    2228700,
    8023320,
    29084535,
    106073010,
    388934370,
    1432916100,
    5301789570,
    19692361260,
    73398801060,
    274447690920
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120590

### Defining data

```json
{
  "b": 1,
  "c": 3,
  "equation": "4*A(x)=3+1*x+A(x)^3",
  "linear_coefficient_d": "1",
  "q": 3,
  "r": 4,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_3": 1
  },
  "classification": "literal_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+3*T^2+1*T^3",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "3": {
      "enumerated": 19,
      "pass": true,
      "published_term": 19
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)"
    ],
    "2": [
      "root[0](Delta_2[0](l,l))",
      "root[0](Delta_2[1](l,l))",
      "root[0](Delta_2[2](l,l))"
    ],
    "3": [
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2[0](l,l),l))",
      "root[0](Delta_2[2](Delta_2[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[1](l,l),l))",
      "root[0](Delta_2[1](Delta_2[1](l,l),l))",
      "root[0](Delta_2[2](Delta_2[1](l,l),l))",
      "root[0](Delta_2[0](Delta_2[2](l,l),l))",
      "root[0](Delta_2[1](Delta_2[2](l,l),l))",
      "root[0](Delta_2[2](Delta_2[2](l,l),l))",
      "root[0](Delta_3[0](l,l,l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-3*u^1-1*u^2",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-1*u^2)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=13",
    "shape": [
      6,
      6
    ]
  },
  "expected_shift_count_for_first_nullvector": 3,
  "integrand": "(1)/(n*(-u**3 - 3*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 2,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `data/matrices.json`

```json
{
  "bases": {
    "G_codomain_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3",
      "u^4",
      "u^5"
    ],
    "G_domain_basis": [
      "a_0",
      "a_1",
      "a_2",
      "b_0",
      "b_1",
      "b_2"
    ],
    "X_columns": [
      "shift r=0",
      "shift r=1",
      "shift r=2"
    ],
    "X_rows": [
      "coefficient of u^0",
      "coefficient of u^1"
    ],
    "coefficient_order": "ascending powers of u",
    "polynomial_space_basis": [
      "1",
      "u^1",
      "u^2"
    ]
  },
  "canonical_source": "data/matrices.json",
  "full_entries_location": "data/matrices.json",
  "matrix_shapes": {
    "G": [
      6,
      6
    ],
    "G_inverse": [
      6,
      6
    ],
    "J": [
      3,
      3
    ],
    "U": [
      3,
      3
    ],
    "V": [
      3,
      3
    ],
    "X": [
      2,
      3
    ],
    "X_full": [
      3,
      3
    ],
    "embedding_E": [
      6,
      3
    ]
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "153*n/(13*n + 13) - 75/(13*n + 13)",
          "25137*n**2/(169*n**2 + 507*n + 338) + 243*n/(169*n**2 + 507*n + 338) - 6114/(169*n**2 + 507*n + 338)"
        ],
        [
          "0",
          "72*n/(13*n + 13) - 48/(13*n + 13)",
          "11664*n**2/(169*n**2 + 507*n + 338) - 1944*n/(169*n**2 + 507*n + 338) - 3888/(169*n**2 + 507*n + 338)"
        ]
      ],
      "shape": [
        2,
        3
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "153*n/(13*n + 13) - 75/(13*n + 13)",
          "25137*n**2/(169*n**2 + 507*n + 338) + 243*n/(169*n**2 + 507*n + 338) - 6114/(169*n**2 + 507*n + 338)"
        ],
        [
          "0",
          "72*n/(13*n + 13) - 48/(13*n + 13)",
          "11664*n**2/(169*n**2 + 507*n + 338) - 1944*n/(169*n**2 + 507*n + 338) - 3888/(169*n**2 + 507*n + 338)"
        ],
        [
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        3,
        3
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `data/recurrence.json`

```json
{
  "legacy_top_level": [
    "-27*n**2 + 3",
    "-162*n**2 - 243*n - 81",
    "13*n**2 + 39*n + 26"
  ],
  "recurrence": {
    "coefficients": [
      "-27*n**2 + 3",
      "-162*n**2 - 243*n - 81",
      "13*n**2 + 39*n + 26"
    ],
    "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
    "order": 2,
    "valid_from_n": 1
  },
  "status": "verified"
}
```

### Rational telescoping certificate

Canonical source: `data/certificate.json`

```json
{
  "denominator_base": "-u**3 - 3*u**2 + u",
  "denominator_power": 1,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-9*n*u**4 - 36*n*u**3 + 6*n*u**2 + 84*n*u - 13*n - 3*u**4 - 12*u**3 - 6*u**2 + 3*u",
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 19,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 20,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "3*x**2",
      "-27*x**3 - 81*x**2",
      "-27*x**4 - 162*x**3 + 13*x**2"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 2
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-27*theta**2 + 3",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-162*theta**2 + 81*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "13*theta**2 - 13*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      22
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        22
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    3,
    19,
    150,
    1326
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    3,
    19,
    150,
    1326,
    12558,
    124590,
    1278189,
    13449205,
    144342627,
    1573990275,
    17389407984,
    194228357568,
    2189610888840,
    24881753664840,
    284708154606318,
    3277578288381318,
    37934510719585350,
    441152315040444150,
    5152282099512304680,
    60406551502736538000,
    710696386643487054660,
    8388096824571665369220
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120591

### Defining data

```json
{
  "observable": "A_parent(x)^3",
  "parent": "A120590",
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "observable power as ordered forest",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "classification": "colored_unweighted",
  "component": "tree_model",
  "model": "ordered forest of 3 parent A120590 typogeometries",
  "parent_branch_multiplicities": {
    "Delta_2": 3,
    "Delta_3": 1
  },
  "status": "verified",
  "top_constructor": "Delta_3 with all 3 positions occupied"
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 12,
      "pass": true,
      "published_term": 12
    },
    "3": {
      "enumerated": 76,
      "pass": true,
      "published_term": 76
    }
  },
  "encoding": "ordered 3-forest; false is the unit parent object",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "16fa162cc8a884cdbb0818144c29af96bb8ca9bdabac96e51e214522b9e50023",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 3,
      "first_five": [
        "Delta_3F(false,false,root[0](l))",
        "Delta_3F(false,root[0](l),false)",
        "Delta_3F(root[0](l),false,false)"
      ],
      "last_five": [
        "Delta_3F(false,false,root[0](l))",
        "Delta_3F(false,root[0](l),false)",
        "Delta_3F(root[0](l),false,false)"
      ]
    },
    "2": {
      "count": 12,
      "first_five": [
        "Delta_3F(false,false,root[0](Delta_2[0](l,l)))",
        "Delta_3F(false,false,root[0](Delta_2[1](l,l)))",
        "Delta_3F(false,false,root[0](Delta_2[2](l,l)))",
        "Delta_3F(false,root[0](l),root[0](l))",
        "Delta_3F(false,root[0](Delta_2[0](l,l)),false)"
      ],
      "last_five": [
        "Delta_3F(root[0](l),false,root[0](l))",
        "Delta_3F(root[0](l),root[0](l),false)",
        "Delta_3F(root[0](Delta_2[0](l,l)),false,false)",
        "Delta_3F(root[0](Delta_2[1](l,l)),false,false)",
        "Delta_3F(root[0](Delta_2[2](l,l)),false,false)"
      ]
    },
    "3": {
      "count": 76,
      "first_five": [
        "Delta_3F(false,false,root[0](Delta_2[0](l,Delta_2[0](l,l))))",
        "Delta_3F(false,false,root[0](Delta_2[1](l,Delta_2[0](l,l))))",
        "Delta_3F(false,false,root[0](Delta_2[2](l,Delta_2[0](l,l))))",
        "Delta_3F(false,false,root[0](Delta_2[0](l,Delta_2[1](l,l))))",
        "Delta_3F(false,false,root[0](Delta_2[1](l,Delta_2[1](l,l))))"
      ],
      "last_five": [
        "Delta_3F(root[0](Delta_2[2](Delta_2[1](l,l),l)),false,false)",
        "Delta_3F(root[0](Delta_2[0](Delta_2[2](l,l),l)),false,false)",
        "Delta_3F(root[0](Delta_2[1](Delta_2[2](l,l),l)),false,false)",
        "Delta_3F(root[0](Delta_2[2](Delta_2[2](l,l),l)),false,false)",
        "Delta_3F(root[0](Delta_3[0](l,l,l)),false,false)"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-3*u^1-1*u^2",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "formula": "[x^n]A(x)^3=(3*1)/(2*pi*i*n)*integral_gamma (1+(1)*u)^2 du/(u^n*D(u)^n)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "invertibility_witness": "resultant(rho,rho')=13",
    "shape": [
      6,
      6
    ]
  },
  "expected_shift_count_for_first_nullvector": 3,
  "integrand": "(3)*(u**2 + 2*u + 1)/(n*(-u**3 - 3*u**2 + u)^n)",
  "kernel_class": "polynomial_power_with_fixed_seed",
  "q3_algorithm_relation": "identical G/U/V and pole lowering; initialize shift 0 with the coefficient vector of the fixed seed instead of e_0",
  "remainder_dimension": 2,
  "required_change": "accept a fixed numerator seed vector and propagate it through every shifted column",
  "seed_degree": 2,
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/matrices",
  "matrix_shapes": {},
  "remainder_matrices": {},
  "statistics": {
    "G_shape": [
      6,
      6
    ],
    "X_shape": [
      3,
      4
    ],
    "certificate_numerator_degree_n": 2,
    "certificate_numerator_degree_u": 6,
    "certificate_parameter_denominator": "n*u**2 + 2*n*u + n + u**2 + 2*u + 1",
    "denominator_degree": 3,
    "leading_zero_coefficients": 1,
    "nullity": 1,
    "rank": 3,
    "recurrence_order": 3,
    "remainder_dimension": 3,
    "shift_columns": 4
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/recurrence`

```json
[
  "0",
  "-27*n**2 - 54*n - 24",
  "-162*n**2 - 567*n - 486",
  "13*n**2 + 65*n + 78"
]
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/certificate`

```json
{
  "N": "-9*n**2*u**6/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 54*n**2*u**5/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 75*n**2*u**4/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 60*n**2*u**3/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 161*n**2*u**2/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 58*n**2*u/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 13*n**2/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 18*n*u**6/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 108*n*u**5/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 142*n*u**4/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 125*n*u**3/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 225*n*u**2/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 35*n*u/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 13*n/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 8*u**6/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 48*u**5/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 56*u**4/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) + 48*u**3/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1) - 8*u**2/(n*u**2 + 2*n*u + n + u**2 + 2*u + 1)",
  "denominator_base": "-u**3 - 3*u**2 + u",
  "denominator_power": 2
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/ode`

```json
{
  "boundary_polynomial": "24*x**3 + 72*x**2",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "3*x**2",
      "-27*x**3 - 81*x**2",
      "-27*x**4 - 162*x**3 + 13*x**2"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 2
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "0",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-27*theta**2 + 3",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-162*theta**2 + 81*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "13*theta**2 - 13*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      21
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        21
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    12,
    76,
    600,
    5304
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    12,
    76,
    600,
    5304,
    50232,
    498360,
    5112756,
    53796820,
    577370508,
    6295961100,
    69557631936,
    776913430272,
    8758443555360,
    99527014659360,
    1138832618425272,
    13110313153525272,
    151738042878341400,
    1764609260161776600,
    20609128398049218720,
    241626206010946152000,
    2842785546573948218640,
    33552387298286661476880
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120592

### Defining data

```json
{
  "b": 4,
  "c": 4,
  "equation": "5*A(x)=4+4*x+A(x)^3",
  "linear_coefficient_d": "2",
  "q": 3,
  "r": 5,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_3": 2
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(2)*T(x)",
  "recursive_equation": "T=x+3*T^2+2*T^3",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    },
    "2": {
      "enumerated": 6,
      "pass": true,
      "published_term": 6
    },
    "3": {
      "enumerated": 40,
      "pass": true,
      "published_term": 40
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)",
      "root[1](l)"
    ],
    "2": [
      "root[0](Delta_2[0](l,l))",
      "root[0](Delta_2[1](l,l))",
      "root[0](Delta_2[2](l,l))",
      "root[1](Delta_2[0](l,l))",
      "root[1](Delta_2[1](l,l))",
      "root[1](Delta_2[2](l,l))"
    ],
    "3": [
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2[0](l,l),l))",
      "root[0](Delta_2[2](Delta_2[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[1](l,l),l))",
      "root[0](Delta_2[1](Delta_2[1](l,l),l))",
      "root[0](Delta_2[2](Delta_2[1](l,l),l))",
      "root[0](Delta_2[0](Delta_2[2](l,l),l))",
      "root[0](Delta_2[1](Delta_2[2](l,l),l))",
      "root[0](Delta_2[2](Delta_2[2](l,l),l))",
      "root[0](Delta_3[0](l,l,l))",
      "root[0](Delta_3[1](l,l,l))",
      "root[1](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[0](Delta_2[0](l,l),l))",
      "root[1](Delta_2[1](Delta_2[0](l,l),l))",
      "root[1](Delta_2[2](Delta_2[0](l,l),l))",
      "root[1](Delta_2[0](Delta_2[1](l,l),l))",
      "root[1](Delta_2[1](Delta_2[1](l,l),l))",
      "root[1](Delta_2[2](Delta_2[1](l,l),l))",
      "root[1](Delta_2[0](Delta_2[2](l,l),l))",
      "root[1](Delta_2[1](Delta_2[2](l,l),l))",
      "root[1](Delta_2[2](Delta_2[2](l,l),l))",
      "root[1](Delta_3[0](l,l,l))",
      "root[1](Delta_3[1](l,l,l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-3*u^1-2*u^2",
  "coefficient_integral": "a(n)=(2)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(2)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-2*u^2)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=34",
    "shape": [
      6,
      6
    ]
  },
  "expected_shift_count_for_first_nullvector": 3,
  "integrand": "(2)/(n*(-2*u**3 - 3*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 2,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-2*u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `runs/A120592-polynomial-pilot/case.json#/objects/matrices`

```json
{
  "canonical_source": "runs/A120592-polynomial-pilot/case.json#/objects/matrices",
  "full_entries_location": "runs/A120592-polynomial-pilot/case.json#/objects/matrices",
  "matrix_shapes": {
    "G": [
      6,
      6
    ],
    "G_inverse": [
      6,
      6
    ],
    "J": [
      3,
      3
    ],
    "U": [
      3,
      3
    ],
    "V": [
      3,
      3
    ],
    "X": [
      2,
      3
    ],
    "X_full": [
      3,
      3
    ],
    "embedding_E": [
      6,
      3
    ]
  },
  "pilot_statistics": {
    "G_determinant": "-68",
    "G_nonzero": 18,
    "G_shape": [
      6,
      6
    ],
    "X_rank": 2,
    "X_shape": [
      2,
      3
    ],
    "certificate_degree_n": 1,
    "certificate_degree_u": 4,
    "certificate_denominator_power": 1,
    "peak_rss_kib": 60048,
    "recurrence_degree": 2,
    "recurrence_order": 2,
    "wall_seconds": 0.531084354000086
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "198*n/(17*n + 17) - 96/(17*n + 17)",
          "44604*n**2/(289*n**2 + 867*n + 578) + 648*n/(289*n**2 + 867*n + 578) - 10572/(289*n**2 + 867*n + 578)"
        ],
        [
          "0",
          "180*n/(17*n + 17) - 120/(17*n + 17)",
          "38880*n**2/(289*n**2 + 867*n + 578) - 6480*n/(289*n**2 + 867*n + 578) - 12960/(289*n**2 + 867*n + 578)"
        ]
      ],
      "shape": [
        2,
        3
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "198*n/(17*n + 17) - 96/(17*n + 17)",
          "44604*n**2/(289*n**2 + 867*n + 578) + 648*n/(289*n**2 + 867*n + 578) - 10572/(289*n**2 + 867*n + 578)"
        ],
        [
          "0",
          "180*n/(17*n + 17) - 120/(17*n + 17)",
          "38880*n**2/(289*n**2 + 867*n + 578) - 6480*n/(289*n**2 + 867*n + 578) - 12960/(289*n**2 + 867*n + 578)"
        ],
        [
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        3,
        3
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `runs/A120592-polynomial-pilot/case.json#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-108*n**2 + 12",
    "-216*n**2 - 324*n - 108",
    "17*n**2 + 51*n + 34"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 2,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `runs/A120592-polynomial-pilot/case.json#/objects/rational_certificate`

```json
{
  "denominator_base": "-2*u**3 - 3*u**2 + u",
  "denominator_power": 1,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-72*n*u**4 - 144*n*u**3 + 42*n*u**2 + 114*n*u - 17*n - 24*u**4 - 48*u**3 - 6*u**2 + 6*u"
}
```

### Scalar linear ODE

Canonical source: `runs/A120592-polynomial-pilot/case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 19,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "12*x**2",
      "-108*x**3 - 108*x**2",
      "-108*x**4 - 216*x**3 + 17*x**2"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 2
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-108*theta**2 + 12",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-216*theta**2 + 108*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "17*theta**2 - 17*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      21
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        21
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    2,
    6,
    40,
    330,
    3048
  ],
  "status": "verified",
  "terms": [
    1,
    2,
    6,
    40,
    330,
    3048,
    30156,
    312528,
    3349170,
    36809960,
    412651668,
    4700098416,
    54237852708,
    632762593680,
    7450815536280,
    88435205367456,
    1056940049423682,
    12708927083800296,
    153636691533864900,
    1866178021496170800,
    22765001791630010220,
    278775897127835688240,
    3425768782722192750120,
    42231822612276216348000
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120593

### Defining data

```json
{
  "b": 1,
  "c": 4,
  "equation": "5*A(x)=4+1*x+A(x)^4",
  "linear_coefficient_d": "1",
  "q": 4,
  "r": 5,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 6,
    "Delta_3": 4,
    "Delta_4": 1
  },
  "classification": "literal_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+6*T^2+4*T^3+1*T^4",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 6,
      "pass": true,
      "published_term": 6
    },
    "3": {
      "enumerated": 76,
      "pass": true,
      "published_term": 76
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "d78389491fde1e0af2b805963efe6b0eca715beb8f7b5716b8504ba163aec335",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 1,
      "first_five": [
        "root[0](l)"
      ],
      "last_five": [
        "root[0](l)"
      ]
    },
    "2": {
      "count": 6,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))",
        "root[0](Delta_2[5](l,l))"
      ]
    },
    "3": {
      "count": 76,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[0](Delta_2[5](Delta_2[5](l,l),l))",
        "root[0](Delta_3[0](l,l,l))",
        "root[0](Delta_3[1](l,l,l))",
        "root[0](Delta_3[2](l,l,l))",
        "root[0](Delta_3[3](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-6*u^1-4*u^2-1*u^3",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-6*u^1-4*u^2-1*u^3)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=491",
    "shape": [
      8,
      8
    ]
  },
  "expected_shift_count_for_first_nullvector": 4,
  "integrand": "(1)/(n*(-u**4 - 4*u**3 - 6*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 3,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**4 - 4*u**3 - 6*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `data/matrices.json`

```json
{
  "bases": {
    "G_codomain_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3",
      "u^4",
      "u^5",
      "u^6",
      "u^7"
    ],
    "G_domain_basis": [
      "a_0",
      "a_1",
      "a_2",
      "a_3",
      "b_0",
      "b_1",
      "b_2",
      "b_3"
    ],
    "X_columns": [
      "shift r=0",
      "shift r=1",
      "shift r=2",
      "shift r=3"
    ],
    "X_rows": [
      "coefficient of u^0",
      "coefficient of u^1",
      "coefficient of u^2"
    ],
    "coefficient_order": "ascending powers of u",
    "polynomial_space_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3"
    ]
  },
  "canonical_source": "data/matrices.json",
  "full_entries_location": "data/matrices.json",
  "matrix_shapes": {
    "G": [
      8,
      8
    ],
    "G_inverse": [
      8,
      8
    ],
    "J": [
      4,
      4
    ],
    "U": [
      4,
      4
    ],
    "V": [
      4,
      4
    ],
    "X": [
      3,
      4
    ],
    "X_full": [
      4,
      4
    ],
    "embedding_E": [
      8,
      4
    ]
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "11536*n/(491*n + 491) - 5644/(491*n + 491)",
          "143231296*n**2/(241081*n**2 + 723243*n + 482162) + 1531568*n/(241081*n**2 + 723243*n + 482162) - 34829928/(241081*n**2 + 723243*n + 482162)",
          "1777488230656*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 2685239289216*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 401187187024*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 649621229544/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ],
        [
          "0",
          "11040*n/(491*n + 491) - 7320/(491*n + 491)",
          "136130880*n**2/(241081*n**2 + 723243*n + 482162) - 22236240*n/(241081*n**2 + 723243*n + 482162) - 45033000/(241081*n**2 + 723243*n + 482162)",
          "1689428459520*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 2258188738560*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 970388551680*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 839939274240/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ],
        [
          "0",
          "3600*n/(491*n + 491) - 2700/(491*n + 491)",
          "44236800*n**2/(241081*n**2 + 723243*n + 482162) - 11059200*n/(241081*n**2 + 723243*n + 482162) - 16588800/(241081*n**2 + 723243*n + 482162)",
          "549011865600*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 686264832000*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 410967014400*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 309413088000/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ]
      ],
      "shape": [
        3,
        4
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "11536*n/(491*n + 491) - 5644/(491*n + 491)",
          "143231296*n**2/(241081*n**2 + 723243*n + 482162) + 1531568*n/(241081*n**2 + 723243*n + 482162) - 34829928/(241081*n**2 + 723243*n + 482162)",
          "1777488230656*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 2685239289216*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 401187187024*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 649621229544/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ],
        [
          "0",
          "11040*n/(491*n + 491) - 7320/(491*n + 491)",
          "136130880*n**2/(241081*n**2 + 723243*n + 482162) - 22236240*n/(241081*n**2 + 723243*n + 482162) - 45033000/(241081*n**2 + 723243*n + 482162)",
          "1689428459520*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 2258188738560*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 970388551680*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 839939274240/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ],
        [
          "0",
          "3600*n/(491*n + 491) - 2700/(491*n + 491)",
          "44236800*n**2/(241081*n**2 + 723243*n + 482162) - 11059200*n/(241081*n**2 + 723243*n + 482162) - 16588800/(241081*n**2 + 723243*n + 482162)",
          "549011865600*n**3/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) + 686264832000*n**2/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 410967014400*n/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626) - 309413088000/(118370771*n**3 + 710224626*n**2 + 1302078481*n + 710224626)"
        ],
        [
          "0",
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        4,
        4
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `data/recurrence.json`

```json
{
  "legacy_top_level": [
    "-256*n**3 - 384*n**2 - 48*n + 40",
    "-3072*n**3 - 9216*n**2 - 8896*n - 2752",
    "-12288*n**3 - 55296*n**2 - 79872*n - 36864",
    "491*n**3 + 2946*n**2 + 5401*n + 2946"
  ],
  "recurrence": {
    "coefficients": [
      "-256*n**3 - 384*n**2 - 48*n + 40",
      "-3072*n**3 - 9216*n**2 - 8896*n - 2752",
      "-12288*n**3 - 55296*n**2 - 79872*n - 36864",
      "491*n**3 + 2946*n**2 + 5401*n + 2946"
    ],
    "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
    "order": 3,
    "valid_from_n": 1
  },
  "status": "verified"
}
```

### Rational telescoping certificate

Canonical source: `data/certificate.json`

```json
{
  "denominator_base": "-u**4 - 4*u**3 - 6*u**2 + u",
  "denominator_power": 2,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "64*n**2*u**9 + 576*n**2*u**8 + 2304*n**2*u**7 + 4496*n**2*u**6 + 2784*n**2*u**5 - 5136*n**2*u**4 - 8524*n**2*u**3 + 204*n**2*u**2 + 6396*n**2*u - 491*n**2 + 112*n*u**9 + 1008*n*u**8 + 4032*n*u**7 + 7988*n*u**6 + 5784*n*u**5 - 6228*n*u**4 - 11872*n*u**3 - 948*n*u**2 + 6648*n*u - 491*n + 40*u**9 + 360*u**8 + 1440*u**7 + 2960*u**6 + 2960*u**5 + 640*u**4 - 440*u**3 + 40*u**2",
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 18,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "40*x**3",
      "-688*x**4 - 2752*x**3",
      "-1152*x**5 - 9216*x**4 - 18432*x**3",
      "-256*x**6 - 3072*x**5 - 12288*x**4 + 491*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-256*theta**3 - 384*theta**2 - 48*theta + 40",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-3072*theta**3 + 320*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-12288*theta**3 + 18432*theta**2 - 6144*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "491*theta**3 - 1473*theta**2 + 982*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      21
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        21
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    6,
    76,
    1201,
    21252
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    6,
    76,
    1201,
    21252,
    402892,
    8001412,
    164321982,
    3461110532,
    74358814838,
    1623152780808,
    35897318940028,
    802620009567628,
    18112759482614328,
    412020809942451504,
    9437537418826749369,
    217486633306640519124,
    5038888894596723858484,
    117303163927569738525484,
    2742468972906020970441060,
    64364604811814815122255960,
    1515891742823217866998084860,
    35815297830647462287712505360
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120594

### Defining data

```json
{
  "b": 8,
  "c": 7,
  "equation": "8*A(x)=7+8*x+A(x)^4",
  "linear_coefficient_d": "2",
  "q": 4,
  "r": 8,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_3": 4,
    "Delta_4": 2
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(2)*T(x)",
  "recursive_equation": "T=x+3*T^2+4*T^3+2*T^4",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    },
    "2": {
      "enumerated": 6,
      "pass": true,
      "published_term": 6
    },
    "3": {
      "enumerated": 44,
      "pass": true,
      "published_term": 44
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)",
      "root[1](l)"
    ],
    "2": [
      "root[0](Delta_2[0](l,l))",
      "root[0](Delta_2[1](l,l))",
      "root[0](Delta_2[2](l,l))",
      "root[1](Delta_2[0](l,l))",
      "root[1](Delta_2[1](l,l))",
      "root[1](Delta_2[2](l,l))"
    ],
    "3": [
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2[0](l,l),l))",
      "root[0](Delta_2[2](Delta_2[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[1](l,l),l))",
      "root[0](Delta_2[1](Delta_2[1](l,l),l))",
      "root[0](Delta_2[2](Delta_2[1](l,l),l))",
      "root[0](Delta_2[0](Delta_2[2](l,l),l))",
      "root[0](Delta_2[1](Delta_2[2](l,l),l))",
      "root[0](Delta_2[2](Delta_2[2](l,l),l))",
      "root[0](Delta_3[0](l,l,l))",
      "root[0](Delta_3[1](l,l,l))",
      "root[0](Delta_3[2](l,l,l))",
      "root[0](Delta_3[3](l,l,l))",
      "root[1](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[1](Delta_2[0](Delta_2[0](l,l),l))",
      "root[1](Delta_2[1](Delta_2[0](l,l),l))",
      "root[1](Delta_2[2](Delta_2[0](l,l),l))",
      "root[1](Delta_2[0](Delta_2[1](l,l),l))",
      "root[1](Delta_2[1](Delta_2[1](l,l),l))",
      "root[1](Delta_2[2](Delta_2[1](l,l),l))",
      "root[1](Delta_2[0](Delta_2[2](l,l),l))",
      "root[1](Delta_2[1](Delta_2[2](l,l),l))",
      "root[1](Delta_2[2](Delta_2[2](l,l),l))",
      "root[1](Delta_3[0](l,l,l))",
      "root[1](Delta_3[1](l,l,l))",
      "root[1](Delta_3[2](l,l,l))",
      "root[1](Delta_3[3](l,l,l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-3*u^1-4*u^2-2*u^3",
  "coefficient_integral": "a(n)=(2)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(2)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-4*u^2-2*u^3)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=712",
    "shape": [
      8,
      8
    ]
  },
  "expected_shift_count_for_first_nullvector": 4,
  "integrand": "(2)/(n*(-2*u**4 - 4*u**3 - 3*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 3,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-2*u**4 - 4*u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      8,
      8
    ],
    "G_inverse": [
      8,
      8
    ],
    "J": [
      4,
      4
    ],
    "U": [
      4,
      4
    ],
    "V": [
      4,
      4
    ],
    "X": [
      3,
      4
    ],
    "X_full": [
      4,
      4
    ],
    "embedding_E": [
      8,
      4
    ]
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "1016*n/(89*n + 89) - 482/(89*n + 89)",
          "1308736*n**2/(7921*n**2 + 23763*n + 15842) + 32000*n/(7921*n**2 + 23763*n + 15842) - 295164/(7921*n**2 + 23763*n + 15842)",
          "1664658944*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 2537730432*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 296343776*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 572952168/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ],
        [
          "0",
          "1824*n/(89*n + 89) - 1200/(89*n + 89)",
          "2213376*n**2/(7921*n**2 + 23763*n + 15842) - 355776*n/(7921*n**2 + 23763*n + 15842) - 714144/(7921*n**2 + 23763*n + 15842)",
          "2821109760*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 3778822656*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1559048064*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1388337216/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ],
        [
          "0",
          "1152*n/(89*n + 89) - 864/(89*n + 89)",
          "1354752*n**2/(7921*n**2 + 23763*n + 15842) - 338688*n/(7921*n**2 + 23763*n + 15842) - 508032/(7921*n**2 + 23763*n + 15842)",
          "1730985984*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 2163732480*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1278144000*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 988751232/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ]
      ],
      "shape": [
        3,
        4
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "1016*n/(89*n + 89) - 482/(89*n + 89)",
          "1308736*n**2/(7921*n**2 + 23763*n + 15842) + 32000*n/(7921*n**2 + 23763*n + 15842) - 295164/(7921*n**2 + 23763*n + 15842)",
          "1664658944*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 2537730432*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 296343776*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 572952168/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ],
        [
          "0",
          "1824*n/(89*n + 89) - 1200/(89*n + 89)",
          "2213376*n**2/(7921*n**2 + 23763*n + 15842) - 355776*n/(7921*n**2 + 23763*n + 15842) - 714144/(7921*n**2 + 23763*n + 15842)",
          "2821109760*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 3778822656*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1559048064*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1388337216/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ],
        [
          "0",
          "1152*n/(89*n + 89) - 864/(89*n + 89)",
          "1354752*n**2/(7921*n**2 + 23763*n + 15842) - 338688*n/(7921*n**2 + 23763*n + 15842) - 508032/(7921*n**2 + 23763*n + 15842)",
          "1730985984*n**3/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) + 2163732480*n**2/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 1278144000*n/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814) - 988751232/(704969*n**3 + 4229814*n**2 + 7754659*n + 4229814)"
        ],
        [
          "0",
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        4,
        4
      ]
    }
  },
  "statistics": {
    "G_nonzero": 32,
    "G_shape": [
      8,
      8
    ],
    "X_rank": 3,
    "X_shape": [
      3,
      4
    ],
    "certificate_degree_n": 2,
    "certificate_degree_u": 9,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 4,
    "nullity": 1,
    "recurrence_degree": 3,
    "recurrence_order": 3
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-512*n**3 - 768*n**2 - 96*n + 80",
    "-1344*n**3 - 4032*n**2 - 3892*n - 1204",
    "-1176*n**3 - 5292*n**2 - 7644*n - 3528",
    "89*n**3 + 534*n**2 + 979*n + 534"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 3,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-2*u**4 - 4*u**3 - 3*u**2 + u",
  "denominator_power": 2,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "512*n**2*u**9 + 2304*n**2*u**8 + 4608*n**2*u**7 + 3968*n**2*u**6 - 192*n**2*u**5 - 3264*n**2*u**4 - 1664*n**2*u**3 + 600*n**2*u**2 + 642*n**2*u - 89*n**2 + 896*n*u**9 + 4032*n*u**8 + 8064*n*u**7 + 7136*n*u**6 + 408*n*u**5 - 4572*n*u**4 - 2420*n*u**3 + 618*n*u**2 + 696*n*u - 89*n + 320*u**9 + 1440*u**8 + 2880*u**7 + 2720*u**6 + 880*u**5 - 440*u**4 - 160*u**3 + 40*u**2"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "80*x**3",
      "-1376*x**4 - 1204*x**3",
      "-2304*x**5 - 4032*x**4 - 1764*x**3",
      "-512*x**6 - 1344*x**5 - 1176*x**4 + 89*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-512*theta**3 - 768*theta**2 - 96*theta + 80",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-1344*theta**3 + 140*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-1176*theta**3 + 1764*theta**2 - 588*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "89*theta**3 - 267*theta**2 + 178*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    2,
    6,
    44,
    394,
    3948
  ],
  "status": "verified",
  "terms": [
    1,
    2,
    6,
    44,
    394,
    3948,
    42364,
    476120,
    5532714,
    65935804,
    801461012,
    9897836520,
    123840983812,
    1566487308344,
    19999112293944,
    257365488659376,
    3334967582746218,
    43477505482249692,
    569854228738577572,
    7504709094221734472,
    99256622233263527340,
    1317823446448750983720,
    17557778766815624932680,
    234671459417445272982480
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120595

### Defining data

```json
{
  "b": 27,
  "c": 12,
  "equation": "13*A(x)=12+27*x+A(x)^4",
  "linear_coefficient_d": "3",
  "q": 4,
  "r": 13,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 2,
    "Delta_3": 4,
    "Delta_4": 3
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(3)*T(x)",
  "recursive_equation": "T=x+2*T^2+4*T^3+3*T^4",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 6,
      "pass": true,
      "published_term": 6
    },
    "3": {
      "enumerated": 36,
      "pass": true,
      "published_term": 36
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)",
      "root[1](l)",
      "root[2](l)"
    ],
    "2": [
      "root[0](Delta_2[0](l,l))",
      "root[0](Delta_2[1](l,l))",
      "root[1](Delta_2[0](l,l))",
      "root[1](Delta_2[1](l,l))",
      "root[2](Delta_2[0](l,l))",
      "root[2](Delta_2[1](l,l))"
    ],
    "3": [
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[1](l,l),l))",
      "root[0](Delta_2[1](Delta_2[1](l,l),l))",
      "root[0](Delta_3[0](l,l,l))",
      "root[0](Delta_3[1](l,l,l))",
      "root[0](Delta_3[2](l,l,l))",
      "root[0](Delta_3[3](l,l,l))",
      "root[1](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[1](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[1](Delta_2[0](Delta_2[0](l,l),l))",
      "root[1](Delta_2[1](Delta_2[0](l,l),l))",
      "root[1](Delta_2[0](Delta_2[1](l,l),l))",
      "root[1](Delta_2[1](Delta_2[1](l,l),l))",
      "root[1](Delta_3[0](l,l,l))",
      "root[1](Delta_3[1](l,l,l))",
      "root[1](Delta_3[2](l,l,l))",
      "root[1](Delta_3[3](l,l,l))",
      "root[2](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[2](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[2](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[2](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[2](Delta_2[0](Delta_2[0](l,l),l))",
      "root[2](Delta_2[1](Delta_2[0](l,l),l))",
      "root[2](Delta_2[0](Delta_2[1](l,l),l))",
      "root[2](Delta_2[1](Delta_2[1](l,l),l))",
      "root[2](Delta_3[0](l,l,l))",
      "root[2](Delta_3[1](l,l,l))",
      "root[2](Delta_3[2](l,l,l))",
      "root[2](Delta_3[3](l,l,l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-2*u^1-4*u^2-3*u^3",
  "coefficient_integral": "a(n)=(3)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(3)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-2*u^1-4*u^2-3*u^3)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=1353",
    "shape": [
      8,
      8
    ]
  },
  "expected_shift_count_for_first_nullvector": 4,
  "integrand": "(3)/(n*(-3*u**4 - 4*u**3 - 2*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 3,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-3*u**4 - 4*u**3 - 2*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      8,
      8
    ],
    "G_inverse": [
      8,
      8
    ],
    "J": [
      4,
      4
    ],
    "U": [
      4,
      4
    ],
    "V": [
      4,
      4
    ],
    "X": [
      3,
      4
    ],
    "X_full": [
      4,
      4
    ],
    "embedding_E": [
      8,
      4
    ]
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "3376*n/(451*n + 451) - 1572/(451*n + 451)",
          "17724736*n**2/(203401*n**2 + 610203*n + 406802) + 540080*n/(203401*n**2 + 610203*n + 406802) - 3619944/(203401*n**2 + 610203*n + 406802)",
          "88038486784*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 134752042112*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 11742815856*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 28313881848/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ],
        [
          "0",
          "8736*n/(451*n + 451) - 5720/(451*n + 451)",
          "39159744*n**2/(203401*n**2 + 610203*n + 406802) - 6382064*n/(203401*n**2 + 610203*n + 406802) - 12136696/(203401*n**2 + 610203*n + 406802)",
          "196708761600*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 263302733824*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 103944595456*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 95866028544/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ],
        [
          "0",
          "8112*n/(451*n + 451) - 6084/(451*n + 451)",
          "33226752*n**2/(203401*n**2 + 610203*n + 406802) - 8306688*n/(203401*n**2 + 610203*n + 406802) - 12460032/(203401*n**2 + 610203*n + 406802)",
          "169813622784*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 212267028480*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 122443176960*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 99207942912/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ]
      ],
      "shape": [
        3,
        4
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "3376*n/(451*n + 451) - 1572/(451*n + 451)",
          "17724736*n**2/(203401*n**2 + 610203*n + 406802) + 540080*n/(203401*n**2 + 610203*n + 406802) - 3619944/(203401*n**2 + 610203*n + 406802)",
          "88038486784*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 134752042112*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 11742815856*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 28313881848/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ],
        [
          "0",
          "8736*n/(451*n + 451) - 5720/(451*n + 451)",
          "39159744*n**2/(203401*n**2 + 610203*n + 406802) - 6382064*n/(203401*n**2 + 610203*n + 406802) - 12136696/(203401*n**2 + 610203*n + 406802)",
          "196708761600*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 263302733824*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 103944595456*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 95866028544/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ],
        [
          "0",
          "8112*n/(451*n + 451) - 6084/(451*n + 451)",
          "33226752*n**2/(203401*n**2 + 610203*n + 406802) - 8306688*n/(203401*n**2 + 610203*n + 406802) - 12460032/(203401*n**2 + 610203*n + 406802)",
          "169813622784*n**3/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) + 212267028480*n**2/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 122443176960*n/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106) - 99207942912/(91733851*n**3 + 550403106*n**2 + 1009072361*n + 550403106)"
        ],
        [
          "0",
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        4,
        4
      ]
    }
  },
  "statistics": {
    "G_nonzero": 32,
    "G_shape": [
      8,
      8
    ],
    "X_rank": 3,
    "X_shape": [
      3,
      4
    ],
    "certificate_degree_n": 2,
    "certificate_degree_u": 9,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 4,
    "nullity": 1,
    "recurrence_degree": 3,
    "recurrence_order": 3
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-6912*n**3 - 10368*n**2 - 1296*n + 1080",
    "-9216*n**3 - 27648*n**2 - 26688*n - 8256",
    "-4096*n**3 - 18432*n**2 - 26624*n - 12288",
    "451*n**3 + 2706*n**2 + 4961*n + 2706"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 3,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-3*u**4 - 4*u**3 - 2*u**2 + u",
  "denominator_power": 2,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "15552*n**2*u**9 + 46656*n**2*u**8 + 62208*n**2*u**7 + 27792*n**2*u**6 - 16992*n**2*u**5 - 26256*n**2*u**4 - 5124*n**2*u**3 + 4780*n**2*u**2 + 2292*n**2*u - 451*n**2 + 27216*n*u**9 + 81648*n*u**8 + 108864*n*u**7 + 51444*n*u**6 - 22392*n*u**5 - 38388*n*u**4 - 7840*n*u**3 + 5612*n*u**2 + 2536*n*u - 451*n + 9720*u**9 + 29160*u**8 + 38880*u**7 + 20880*u**6 - 720*u**5 - 5760*u**4 - 360*u**3 + 360*u**2"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 17,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "1080*x**3",
      "-18576*x**4 - 8256*x**3",
      "-31104*x**5 - 27648*x**4 - 6144*x**3",
      "-6912*x**6 - 9216*x**5 - 4096*x**4 + 451*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-6912*theta**3 - 10368*theta**2 - 1296*theta + 1080",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-9216*theta**3 + 960*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-4096*theta**3 + 6144*theta**2 - 2048*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "451*theta**3 - 1353*theta**2 + 902*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    6,
    36,
    249,
    1932
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    6,
    36,
    249,
    1932,
    16044,
    139500,
    1253934,
    11558316,
    108658902,
    1037800920,
    10041891132,
    98230257636,
    969814634424,
    9651213968784,
    96710160474513,
    974967422602428,
    9881687141571732,
    100632995795535588,
    1029207741601055940,
    10566616122403953480,
    108863382749273728380,
    1125135184501040595120
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120596

### Defining data

```json
{
  "b": 1,
  "c": 5,
  "equation": "6*A(x)=5+1*x+A(x)^5",
  "linear_coefficient_d": "1",
  "q": 5,
  "r": 6,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 10,
    "Delta_3": 10,
    "Delta_4": 5,
    "Delta_5": 1
  },
  "classification": "literal_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+10*T^2+10*T^3+5*T^4+1*T^5",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 10,
      "pass": true,
      "published_term": 10
    },
    "3": {
      "enumerated": 210,
      "pass": true,
      "published_term": 210
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "a01abf335d6b84537e266072abc52f6c00a3e082c216056a4713e284968755d3",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 1,
      "first_five": [
        "root[0](l)"
      ],
      "last_five": [
        "root[0](l)"
      ]
    },
    "2": {
      "count": 10,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[0](Delta_2[5](l,l))",
        "root[0](Delta_2[6](l,l))",
        "root[0](Delta_2[7](l,l))",
        "root[0](Delta_2[8](l,l))",
        "root[0](Delta_2[9](l,l))"
      ]
    },
    "3": {
      "count": 210,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[0](Delta_3[5](l,l,l))",
        "root[0](Delta_3[6](l,l,l))",
        "root[0](Delta_3[7](l,l,l))",
        "root[0](Delta_3[8](l,l,l))",
        "root[0](Delta_3[9](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-10*u^1-10*u^2-5*u^3-1*u^4",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-10*u^1-10*u^2-5*u^3-1*u^4)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=37531",
    "shape": [
      10,
      10
    ]
  },
  "expected_shift_count_for_first_nullvector": 5,
  "integrand": "(1)/(n*(-u**5 - 5*u**4 - 10*u**3 - 10*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 4,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**5 - 5*u**4 - 10*u**3 - 10*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `data/matrices.json`

```json
{
  "bases": {
    "G_codomain_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3",
      "u^4",
      "u^5",
      "u^6",
      "u^7",
      "u^8",
      "u^9"
    ],
    "G_domain_basis": [
      "a_0",
      "a_1",
      "a_2",
      "a_3",
      "a_4",
      "b_0",
      "b_1",
      "b_2",
      "b_3",
      "b_4"
    ],
    "X_columns": [
      "shift r=0",
      "shift r=1",
      "shift r=2",
      "shift r=3",
      "shift r=4"
    ],
    "X_rows": [
      "coefficient of u^0",
      "coefficient of u^1",
      "coefficient of u^2",
      "coefficient of u^3"
    ],
    "coefficient_order": "ascending powers of u",
    "polynomial_space_basis": [
      "1",
      "u^1",
      "u^2",
      "u^3",
      "u^4"
    ]
  },
  "canonical_source": "data/matrices.json",
  "full_entries_location": "data/matrices.json",
  "matrix_shapes": {
    "G": [
      10,
      10
    ],
    "G_inverse": [
      10,
      10
    ],
    "J": [
      5,
      5
    ],
    "U": [
      5,
      5
    ],
    "V": [
      5,
      5
    ],
    "X": [
      4,
      5
    ],
    "X_full": [
      5,
      5
    ],
    "embedding_E": [
      10,
      5
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 20,
      "full_entries_location": "data/matrices.json",
      "full_object_sha256": "4ed6b6018e6fdedfc7b72f294d7a9bb4f6ad1afa3f66be38ea0aee5a832fc19f",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "1337389868990757600000000*n**4/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 4948342515265803120000000*n**3/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 2878251920000969760000000*n**2/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 3642382801830225816000000*n/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 2009521245491145504000000/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504)",
        "top_left": "1",
        "top_right": "5735545712766374939190625*n**4/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 23000542509953386238481250*n**3/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 20355524270300612105954375*n**2/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 5362684384212423662616250*n/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 5253289692965431052955480/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504)"
      },
      "shape": [
        4,
        5
      ]
    },
    "X_full": {
      "entry_count": 25,
      "full_entries_location": "data/matrices.json",
      "full_object_sha256": "e2373318d3ea252d4d97d31269e3d9846db6c09330135afa0aed0c38ee1f537a",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "5735545712766374939190625*n**4/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 23000542509953386238481250*n**3/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) + 20355524270300612105954375*n**2/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 5362684384212423662616250*n/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504) - 5253289692965431052955480/(1984086237907073521*n**4 + 19840862379070735210*n**3 + 69443018326747573235*n**2 + 99204311895353676050*n + 47618069709769764504)"
      },
      "shape": [
        5,
        5
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `data/recurrence.json`

```json
{
  "legacy_top_level": [
    "-3125*n**4 - 12500*n**3 - 13750*n**2 - 2500*n + 1155",
    "-62500*n**4 - 343750*n**3 - 668750*n**2 - 546875*n - 159375",
    "-468750*n**4 - 3281250*n**3 - 8390625*n**2 - 9234375*n - 3656250",
    "-1562500*n**4 - 13281250*n**3 - 40625000*n**2 - 52343750*n - 23437500",
    "37531*n**4 + 375310*n**3 + 1313585*n**2 + 1876550*n + 900744"
  ],
  "recurrence": {
    "coefficients": [
      "-3125*n**4 - 12500*n**3 - 13750*n**2 - 2500*n + 1155",
      "-62500*n**4 - 343750*n**3 - 668750*n**2 - 546875*n - 159375",
      "-468750*n**4 - 3281250*n**3 - 8390625*n**2 - 9234375*n - 3656250",
      "-1562500*n**4 - 13281250*n**3 - 40625000*n**2 - 52343750*n - 23437500",
      "37531*n**4 + 375310*n**3 + 1313585*n**2 + 1876550*n + 900744"
    ],
    "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
    "order": 4,
    "valid_from_n": 1
  },
  "status": "verified"
}
```

### Rational telescoping certificate

Canonical source: `data/certificate.json`

```json
{
  "denominator_base": "-u**5 - 5*u**4 - 10*u**3 - 10*u**2 + u",
  "denominator_power": 3,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-625*n**3*u**16 - 10000*n**3*u**15 - 75000*n**3*u**14 - 350000*n**3*u**13 - 1123250*n**3*u**12 - 2559000*n**3*u**11 - 4064500*n**3*u**10 - 4015000*n**3*u**9 - 1107900*n**3*u**8 + 3192800*n**3*u**7 + 4860800*n**3*u**6 + 1953600*n**3*u**5 - 1938230*n**3*u**4 - 2223320*n**3*u**3 - 44580*n**3*u**2 + 811880*n**3*u - 37531*n**3 - 2625*n**2*u**16 - 42000*n**2*u**15 - 315000*n**2*u**14 - 1470000*n**2*u**13 - 4719450*n**2*u**12 - 10773150*n**2*u**11 - 17230950*n**2*u**10 - 17465250*n**2*u**9 - 6126930*n**2*u**8 + 11088660*n**2*u**7 + 18405660*n**2*u**6 + 8197020*n**2*u**5 - 6093210*n**2*u**4 - 7586670*n**2*u**3 - 385350*n**2*u**2 + 2466270*n**2*u - 112593*n**2 - 3275*n*u**16 - 52400*n*u**15 - 393000*n*u**14 - 1834000*n*u**13 - 5892310*n*u**12 - 13503420*n*u**11 - 21907160*n*u**10 - 23371700*n*u**9 - 11613960*n*u**8 + 7346800*n*u**7 + 16781005*n*u**6 + 8745870*n*u**5 - 3750415*n*u**4 - 5509120*n*u**3 - 332955*n*u**2 + 1654390*n*u - 75062*n - 1155*u**16 - 18480*u**15 - 138600*u**14 - 646800*u**13 - 2081310*u**12 - 4812885*u**11 - 8067675*u**10 - 9592275*u**9 - 7557165*u**8 - 3254790*u**7 - 167475*u**6 + 277200*u**5 - 33495*u**4 + 1155*u**3",
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "1155*x**4",
      "-31875*x**5 - 159375*x**4",
      "-73125*x**6 - 731250*x**5 - 1828125*x**4",
      "-31250*x**7 - 468750*x**6 - 2343750*x**5 - 3906250*x**4",
      "-3125*x**8 - 62500*x**7 - 468750*x**6 - 1562500*x**5 + 37531*x**4"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 4
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-3125*theta**4 - 12500*theta**3 - 13750*theta**2 - 2500*theta + 1155",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-62500*theta**4 - 93750*theta**3 - 12500*theta**2 + 9375*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-468750*theta**4 + 468750*theta**3 + 46875*theta**2 - 46875*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-1562500*theta**4 + 5468750*theta**3 - 5468750*theta**2 + 1562500*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "37531*theta**4 - 225186*theta**3 + 412841*theta**2 - 225186*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    10,
    210,
    5505,
    161601
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    10,
    210,
    5505,
    161601,
    5082420,
    167451780,
    5705082795,
    199354509755,
    7105393162010,
    257312347583330,
    9440808323869455,
    350189693739455535,
    13110655796699158800,
    494772468434359266960,
    18801468275832345890970,
    718807266442025945527410,
    27628770793554335524862400,
    1067046805051507456543264800,
    41386860903398711763315461880,
    1611442977119952377385829586280,
    62962669778169113763428387089800,
    2467917647654372656114814183593800
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120597

### Defining data

```json
{
  "b": 8,
  "c": 8,
  "equation": "9*A(x)=8+8*x+A(x)^5",
  "linear_coefficient_d": "2",
  "q": 5,
  "r": 9,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 5,
    "Delta_3": 10,
    "Delta_4": 10,
    "Delta_5": 4
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(2)*T(x)",
  "recursive_equation": "T=x+5*T^2+10*T^3+10*T^4+4*T^5",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    },
    "2": {
      "enumerated": 10,
      "pass": true,
      "published_term": 10
    },
    "3": {
      "enumerated": 120,
      "pass": true,
      "published_term": 120
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "31f69dfff1e120b55fae92aa5e7ccd94180ace1dc10b241e889787fba4330c12",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 2,
      "first_five": [
        "root[0](l)",
        "root[1](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)"
      ]
    },
    "2": {
      "count": 10,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[1](Delta_2[0](l,l))",
        "root[1](Delta_2[1](l,l))",
        "root[1](Delta_2[2](l,l))",
        "root[1](Delta_2[3](l,l))",
        "root[1](Delta_2[4](l,l))"
      ]
    },
    "3": {
      "count": 120,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[1](Delta_3[5](l,l,l))",
        "root[1](Delta_3[6](l,l,l))",
        "root[1](Delta_3[7](l,l,l))",
        "root[1](Delta_3[8](l,l,l))",
        "root[1](Delta_3[9](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-5*u^1-10*u^2-10*u^3-4*u^4",
  "coefficient_integral": "a(n)=(2)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(2)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-5*u^1-10*u^2-10*u^3-4*u^4)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=579136",
    "shape": [
      10,
      10
    ]
  },
  "expected_shift_count_for_first_nullvector": 5,
  "integrand": "(2)/(n*(-4*u**5 - 10*u**4 - 10*u**3 - 5*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 4,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-4*u**5 - 10*u**4 - 10*u**3 - 5*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      10,
      10
    ],
    "G_inverse": [
      10,
      10
    ],
    "J": [
      5,
      5
    ],
    "U": [
      5,
      5
    ],
    "V": [
      5,
      5
    ],
    "X": [
      4,
      5
    ],
    "X_full": [
      5,
      5
    ],
    "embedding_E": [
      10,
      5
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 20,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "4e66421b1701fe39c2c7c59a7434294435c4419beed5e23090f09ff586006876",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "2654218106266320000000*n**4/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 9820606993185384000000*n**3/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 5756214293892432000000*n**2/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 7197992583781831200000*n/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 4040901597903292800000/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224)",
        "top_left": "1",
        "top_right": "1676783963130772450000*n**4/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 6750112429194932800000*n**3/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 6109383713456933780000*n**2/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 1333349178800073940000*n/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 1452455917791883913520/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224)"
      },
      "shape": [
        4,
        5
      ]
    },
    "X_full": {
      "entry_count": 25,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "3c9a69277d7695ba49b44862c788edeeb57a95abe5368407f108104d7fe45fce",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "1676783963130772450000*n**4/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 6750112429194932800000*n**3/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) + 6109383713456933780000*n**2/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 1333349178800073940000*n/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224) - 1452455917791883913520/(6705055127128801*n**4 + 67050551271288010*n**3 + 234676929449508035*n**2 + 335252756356440050*n + 160921323051091224)"
      },
      "shape": [
        5,
        5
      ]
    }
  },
  "statistics": {
    "G_nonzero": 50,
    "G_shape": [
      10,
      10
    ],
    "X_rank": 4,
    "X_shape": [
      4,
      5
    ],
    "certificate_degree_n": 3,
    "certificate_degree_u": 16,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 5,
    "nullity": 1,
    "recurrence_degree": 4,
    "recurrence_order": 4
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-50000*n**4 - 200000*n**3 - 220000*n**2 - 40000*n + 18480",
    "-200000*n**4 - 1100000*n**3 - 2140000*n**2 - 1750000*n - 510000",
    "-300000*n**4 - 2100000*n**3 - 5370000*n**2 - 5910000*n - 2340000",
    "-200000*n**4 - 1700000*n**3 - 5200000*n**2 - 6700000*n - 3000000",
    "9049*n**4 + 90490*n**3 + 316715*n**2 + 452450*n + 217176"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 4,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-4*u**5 - 10*u**4 - 10*u**3 - 5*u**2 + u",
  "denominator_power": 3,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-640000*n**3*u**16 - 5120000*n**3*u**15 - 19200000*n**3*u**14 - 44800000*n**3*u**13 - 71432000*n**3*u**12 - 79152000*n**3*u**11 - 57508000*n**3*u**10 - 19580000*n**3*u**9 + 9086400*n**3*u**8 + 15313600*n**3*u**7 + 7317800*n**3*u**6 - 328200*n**3*u**5 - 1945280*n**3*u**4 - 640360*n**3*u**3 + 123630*n**3*u**2 + 109510*n**3*u - 9049*n**3 - 2688000*n**2*u**16 - 21504000*n**2*u**15 - 80640000*n**2*u**14 - 188160000*n**2*u**13 - 300187200*n**2*u**12 - 333667200*n**2*u**11 - 245440800*n**2*u**10 - 89628000*n**2*u**9 + 29180880*n**2*u**8 + 57635520*n**2*u**7 + 28643160*n**2*u**6 - 204840*n**2*u**5 - 6645360*n**2*u**4 - 2240160*n**2*u**3 + 365700*n**2*u**2 + 338040*n**2*u - 27147*n**2 - 3353600*n*u**16 - 26828800*n*u**15 - 100608000*n*u**14 - 234752000*n*u**13 - 374925760*n*u**12 - 419333760*n*u**11 - 316252640*n*u**10 - 131322400*n*u**9 + 12036960*n*u**8 + 52860800*n*u**7 + 28461880*n*u**6 + 1323960*n*u**5 - 5052640*n*u**4 - 1684160*n*u**3 + 254430*n*u**2 + 228530*n*u - 18098*n - 1182720*u**16 - 9461760*u**15 - 35481600*u**14 - 82790400*u**13 - 132538560*u**12 - 150353280*u**11 - 119935200*u**10 - 63016800*u**9 - 17130960*u**8 + 1182720*u**7 + 2171400*u**6 + 138600*u**5 - 120120*u**4 + 9240*u**3"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "18480*x**4",
      "-510000*x**5 - 510000*x**4",
      "-1170000*x**6 - 2340000*x**5 - 1170000*x**4",
      "-500000*x**7 - 1500000*x**6 - 1500000*x**5 - 500000*x**4",
      "-50000*x**8 - 200000*x**7 - 300000*x**6 - 200000*x**5 + 9049*x**4"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 4
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-50000*theta**4 - 200000*theta**3 - 220000*theta**2 - 40000*theta + 18480",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-200000*theta**4 - 300000*theta**3 - 40000*theta**2 + 30000*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-300000*theta**4 + 300000*theta**3 + 30000*theta**2 - 30000*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-200000*theta**4 + 700000*theta**3 - 700000*theta**2 + 200000*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "9049*theta**4 - 54294*theta**3 + 99539*theta**2 - 54294*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      19
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        19
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    2,
    10,
    120,
    1770,
    29208
  ],
  "status": "verified",
  "terms": [
    1,
    2,
    10,
    120,
    1770,
    29208,
    516180,
    9554640,
    182867970,
    3589443160,
    71861735660,
    1461730482160,
    30123451315620,
    627598216410480,
    13197173403868200,
    279728425129963680,
    5970277970921643570,
    128199003794219752920,
    2767586952164186091900,
    60032874136166490663600,
    1307774300507798215432620,
    28598864418990745183711440,
    627595137465126647592130200,
    13816208286802971319401986400
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120598

### Defining data

```json
{
  "b": 125,
  "c": 29,
  "equation": "30*A(x)=29+125*x+A(x)^5",
  "linear_coefficient_d": "5",
  "q": 5,
  "r": 30,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 2,
    "Delta_3": 10,
    "Delta_4": 25,
    "Delta_5": 25
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(5)*T(x)",
  "recursive_equation": "T=x+2*T^2+10*T^3+25*T^4+25*T^5",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 5,
      "pass": true,
      "published_term": 5
    },
    "2": {
      "enumerated": 10,
      "pass": true,
      "published_term": 10
    },
    "3": {
      "enumerated": 90,
      "pass": true,
      "published_term": 90
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "3f8db4f2351206e2f17966999067bc5b66ef9a3949e37b1424a01f3f45f0ae7a",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 5,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)",
        "root[4](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)",
        "root[4](l)"
      ]
    },
    "2": {
      "count": 10,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[1](Delta_2[0](l,l))",
        "root[1](Delta_2[1](l,l))",
        "root[2](Delta_2[0](l,l))"
      ],
      "last_five": [
        "root[2](Delta_2[1](l,l))",
        "root[3](Delta_2[0](l,l))",
        "root[3](Delta_2[1](l,l))",
        "root[4](Delta_2[0](l,l))",
        "root[4](Delta_2[1](l,l))"
      ]
    },
    "3": {
      "count": 90,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
        "root[0](Delta_2[0](Delta_2[0](l,l),l))"
      ],
      "last_five": [
        "root[4](Delta_3[5](l,l,l))",
        "root[4](Delta_3[6](l,l,l))",
        "root[4](Delta_3[7](l,l,l))",
        "root[4](Delta_3[8](l,l,l))",
        "root[4](Delta_3[9](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-2*u^1-10*u^2-25*u^3-25*u^4",
  "coefficient_integral": "a(n)=(5)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(5)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-2*u^1-10*u^2-25*u^3-25*u^4)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=160421875",
    "shape": [
      10,
      10
    ]
  },
  "expected_shift_count_for_first_nullvector": 5,
  "integrand": "(5)/(n*(-25*u**5 - 25*u**4 - 10*u**3 - 2*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 4,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-25*u**5 - 25*u**4 - 10*u**3 - 2*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      10,
      10
    ],
    "G_inverse": [
      10,
      10
    ],
    "J": [
      5,
      5
    ],
    "U": [
      5,
      5
    ],
    "V": [
      5,
      5
    ],
    "X": [
      4,
      5
    ],
    "X_full": [
      5,
      5
    ],
    "embedding_E": [
      10,
      5
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 20,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "847d405c5a9e5a1fc57e331a08f28b50773dd1ebd1ae4819fda024b42bf83c6a",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "4117898484517448448000*n**4/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 15236224392714559257600*n**3/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 9329554818370035763200*n**2/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 10888022216649781900800*n/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 6748135418765198592000/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504)",
        "top_left": "1",
        "top_right": "291096485660206629841*n**4/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 1175780208036700347394*n**3/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 1118806009709838029591*n**2/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 125821211196610402906*n/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 207774595687471127640/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504)"
      },
      "shape": [
        4,
        5
      ]
    },
    "X_full": {
      "entry_count": 25,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "b2f8082159af6883c171b4601f17794091a06cd99cee8577addcfebf25100985",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "291096485660206629841*n**4/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 1175780208036700347394*n**3/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) + 1118806009709838029591*n**2/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 125821211196610402906*n/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504) - 207774595687471127640/(11111539848641521*n**4 + 111115398486415210*n**3 + 388903894702453235*n**2 + 555576992432076050*n + 266676956367396504)"
      },
      "shape": [
        5,
        5
      ]
    }
  },
  "statistics": {
    "G_nonzero": 50,
    "G_shape": [
      10,
      10
    ],
    "X_rank": 4,
    "X_shape": [
      4,
      5
    ],
    "certificate_degree_n": 3,
    "certificate_degree_u": 16,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 5,
    "nullity": 1,
    "recurrence_degree": 4,
    "recurrence_order": 4
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-1953125*n**4 - 7812500*n**3 - 8593750*n**2 - 1562500*n + 721875",
    "-1812500*n**4 - 9968750*n**3 - 19393750*n**2 - 15859375*n - 4621875",
    "-630750*n**4 - 4415250*n**3 - 11290425*n**2 - 12425775*n - 4919850",
    "-97556*n**4 - 829226*n**3 - 2536456*n**2 - 3268126*n - 1463340",
    "10267*n**4 + 102670*n**3 + 359345*n**2 + 513350*n + 246408"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 4,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-25*u**5 - 25*u**4 - 10*u**3 - 2*u**2 + u",
  "denominator_power": 3,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-6103515625*n**3*u**16 - 19531250000*n**3*u**15 - 29296875000*n**3*u**14 - 27343750000*n**3*u**13 - 16660156250*n**3*u**12 - 5859375000*n**3*u**11 - 189062500*n**3*u**10 + 1065625000*n**3*u**9 + 606937500*n**3*u**8 + 128500000*n**3*u**7 - 21700000*n**3*u**6 - 22272000*n**3*u**5 - 4895150*n**3*u**4 + 396200*n**3*u**3 + 353580*n**3*u**2 + 56488*n**3*u - 10267*n**3 - 25634765625*n**2*u**16 - 82031250000*n**2*u**15 - 123046875000*n**2*u**14 - 114843750000*n**2*u**13 - 70113281250*n**2*u**12 - 25014843750*n**2*u**11 - 1314843750*n**2*u**10 + 4078593750*n**2*u**9 + 2370543750*n**2*u**8 + 512002500*n**2*u**7 - 73342500*n**2*u**6 - 80320500*n**2*u**5 - 17483250*n**2*u**4 + 1288650*n**2*u**3 + 1152570*n**2*u**2 + 177174*n**2*u - 30801*n**2 - 31982421875*n*u**16 - 102343750000*n*u**15 - 153515625000*n*u**14 - 143281250000*n*u**13 - 87805468750*n*u**12 - 32217187500*n*u**11 - 2985125000*n*u**10 + 4034937500*n*u**9 + 2460600000*n*u**8 + 540770000*n*u**7 - 58911875*n*u**6 - 70970250*n*u**5 - 14301775*n*u**4 + 1132000*n*u**3 + 843165*n*u**2 + 120686*n*u - 20534*n - 11279296875*u**16 - 36093750000*u**15 - 54140625000*u**14 - 50531250000*u**13 - 31221093750*u**12 - 12181640625*u**11 - 2183671875*u**10 + 516140625*u**9 + 422296875*u**8 + 85181250*u**7 - 7651875*u**6 - 6930000*u**5 - 144375*u**4 + 144375*u**3"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "721875*x**4",
      "-19921875*x**5 - 4621875*x**4",
      "-45703125*x**6 - 21206250*x**5 - 2459925*x**4",
      "-19531250*x**7 - 13593750*x**6 - 3153750*x**5 - 243890*x**4",
      "-1953125*x**8 - 1812500*x**7 - 630750*x**6 - 97556*x**5 + 10267*x**4"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 4
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-1953125*theta**4 - 7812500*theta**3 - 8593750*theta**2 - 1562500*theta + 721875",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-1812500*theta**4 - 2718750*theta**3 - 362500*theta**2 + 271875*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-630750*theta**4 + 630750*theta**3 + 63075*theta**2 - 63075*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-97556*theta**4 + 341446*theta**3 - 341446*theta**2 + 97556*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "10267*theta**4 - 61602*theta**3 + 112937*theta**2 - 61602*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      19
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        19
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    5,
    10,
    90,
    825,
    8445
  ],
  "status": "verified",
  "terms": [
    1,
    5,
    10,
    90,
    825,
    8445,
    92820,
    1066740,
    12670635,
    154308775,
    1916370170,
    24177471370,
    309007779015,
    3992428316835,
    52059968802000,
    684240882022800,
    9055282215370050,
    120563388411386850,
    1613785688724362400,
    21703989380492544000,
    293144944889582574600,
    3974586258490943112600,
    54076852182469177780200,
    738083059816046793193800
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120599

### Defining data

```json
{
  "b": 32,
  "c": 12,
  "equation": "13*A(x)=12+32*x+A(x)^5",
  "linear_coefficient_d": "4",
  "q": 5,
  "r": 13,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 5,
    "Delta_3": 20,
    "Delta_4": 40,
    "Delta_5": 32
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(4)*T(x)",
  "recursive_equation": "T=x+5*T^2+20*T^3+40*T^4+32*T^5",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 4,
      "pass": true,
      "published_term": 4
    },
    "2": {
      "enumerated": 20,
      "pass": true,
      "published_term": 20
    },
    "3": {
      "enumerated": 280,
      "pass": true,
      "published_term": 280
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "cdad4cfea9d11210cfde7831abf782bdf38633df54f1aae1cd3150bc754c50da",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 4,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ]
    },
    "2": {
      "count": 20,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[3](Delta_2[0](l,l))",
        "root[3](Delta_2[1](l,l))",
        "root[3](Delta_2[2](l,l))",
        "root[3](Delta_2[3](l,l))",
        "root[3](Delta_2[4](l,l))"
      ]
    },
    "3": {
      "count": 280,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[3](Delta_3[15](l,l,l))",
        "root[3](Delta_3[16](l,l,l))",
        "root[3](Delta_3[17](l,l,l))",
        "root[3](Delta_3[18](l,l,l))",
        "root[3](Delta_3[19](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-5*u^1-20*u^2-40*u^3-32*u^4",
  "coefficient_integral": "a(n)=(4)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(4)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-5*u^1-20*u^2-40*u^3-32*u^4)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=968032256",
    "shape": [
      10,
      10
    ]
  },
  "expected_shift_count_for_first_nullvector": 5,
  "integrand": "(4)/(n*(-32*u**5 - 40*u**4 - 20*u**3 - 5*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 4,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-32*u**5 - 40*u**4 - 20*u**3 - 5*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      10,
      10
    ],
    "G_inverse": [
      10,
      10
    ],
    "J": [
      5,
      5
    ],
    "U": [
      5,
      5
    ],
    "V": [
      5,
      5
    ],
    "X": [
      4,
      5
    ],
    "X_full": [
      5,
      5
    ],
    "embedding_E": [
      10,
      5
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 20,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "8b5d7d9b5c667352881a47959394b21269b1accef834921d0a180cdab1f1a3fc",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "184291639920847680000000*n**4/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 681879067707136416000000*n**3/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 404152564826653968000000*n**2/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 496646841486527908800000*n/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 285948106677469267200000/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544)",
        "top_left": "1",
        "top_right": "17075065969461737600000*n**4/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 68872489098566644400000*n**3/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 63436665961172441440000*n**2/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 11534405174961561620000*n/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 13992923613659489214960/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544)"
      },
      "shape": [
        4,
        5
      ]
    },
    "X_full": {
      "entry_count": 25,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "978aa61ed8f964f45e39e21c8f741a7ce7bfb5f919d1fb512b32857ec280f4f8",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "17075065969461737600000*n**4/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 68872489098566644400000*n**3/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) + 63436665961172441440000*n**2/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 11534405174961561620000*n/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544) - 13992923613659489214960/(47603577560718481*n**4 + 476035775607184810*n**3 + 1666125214625146835*n**2 + 2380178878035924050*n + 1142485861457243544)"
      },
      "shape": [
        5,
        5
      ]
    }
  },
  "statistics": {
    "G_nonzero": 50,
    "G_shape": [
      10,
      10
    ],
    "X_rank": 4,
    "X_shape": [
      4,
      5
    ],
    "certificate_degree_n": 3,
    "certificate_degree_u": 16,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 5,
    "nullity": 1,
    "recurrence_degree": 4,
    "recurrence_order": 4
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-1600000*n**4 - 6400000*n**3 - 7040000*n**2 - 1280000*n + 591360",
    "-2400000*n**4 - 13200000*n**3 - 25680000*n**2 - 21000000*n - 6120000",
    "-1350000*n**4 - 9450000*n**3 - 24165000*n**2 - 26595000*n - 10530000",
    "-337500*n**4 - 2868750*n**3 - 8775000*n**2 - 11306250*n - 5062500",
    "14771*n**4 + 147710*n**3 + 516985*n**2 + 738550*n + 354504"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 4,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-32*u**5 - 40*u**4 - 20*u**3 - 5*u**2 + u",
  "denominator_power": 3,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-10485760000*n**3*u**16 - 41943040000*n**3*u**15 - 78643200000*n**3*u**14 - 91750400000*n**3*u**13 - 72523776000*n**3*u**12 - 38658048000*n**3*u**11 - 12153856000*n**3*u**10 - 366080000*n**3*u**9 + 1711590400*n**3*u**8 + 824012800*n**3*u**7 + 128419200*n**3*u**6 - 37086400*n**3*u**5 - 20544160*n**3*u**4 - 2084560*n**3*u**3 + 674140*n**3*u**2 + 189790*n**3*u - 14771*n**3 - 44040192000*n**2*u**16 - 176160768000*n**2*u**15 - 330301440000*n**2*u**14 - 385351680000*n**2*u**13 - 304855449600*n**2*u**12 - 163278028800*n**2*u**11 - 52506009600*n**2*u**10 - 2923008000*n**2*u**9 + 6357575680*n**2*u**8 + 3177589760*n**2*u**7 + 522336640*n**2*u**6 - 123306880*n**2*u**5 - 71909520*n**2*u**4 - 7472360*n**2*u**3 + 2125900*n**2*u**2 + 590410*n**2*u - 44313*n**2 - 54945382400*n*u**16 - 219781529600*n*u**15 - 412090368000*n*u**14 - 480772096000*n*u**13 - 380944711680*n*u**12 - 205977354240*n*u**11 - 69265940480*n*u**10 - 7311462400*n*u**9 + 5662940160*n*u**8 + 3135616000*n*u**7 + 554235520*n*u**6 - 91889280*n*u**5 - 57512480*n*u**4 - 5616760*n*u**3 + 1525440*n*u**2 + 400620*n*u - 29542*n - 19377684480*u**16 - 77510737920*u**15 - 145332633600*u**14 - 169554739200*u**13 - 134811156480*u**12 - 74482974720*u**11 - 27581030400*u**10 - 5724364800*u**9 - 3548160*u**8 + 328796160*u**7 + 61353600*u**6 - 6652800*u**5 - 1626240*u**4 + 147840*u**3"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "591360*x**4",
      "-16320000*x**5 - 6120000*x**4",
      "-37440000*x**6 - 28080000*x**5 - 5265000*x**4",
      "-16000000*x**7 - 18000000*x**6 - 6750000*x**5 - 843750*x**4",
      "-1600000*x**8 - 2400000*x**7 - 1350000*x**6 - 337500*x**5 + 14771*x**4"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 4
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-1600000*theta**4 - 6400000*theta**3 - 7040000*theta**2 - 1280000*theta + 591360",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-2400000*theta**4 - 3600000*theta**3 - 480000*theta**2 + 360000*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-1350000*theta**4 + 1350000*theta**3 + 135000*theta**2 - 135000*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-337500*theta**4 + 1181250*theta**3 - 1181250*theta**2 + 337500*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "14771*theta**4 - 88626*theta**3 + 162481*theta**2 - 88626*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      19
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        19
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    4,
    20,
    280,
    4660,
    86728
  ],
  "status": "verified",
  "terms": [
    1,
    4,
    20,
    280,
    4660,
    86728,
    1727880,
    36047280,
    777470580,
    17195957480,
    387906427480,
    8890184148560,
    206419640698440,
    4845319424269520,
    114791477960006800,
    2741248077305459040,
    65915164046356799220,
    1594598219827695833640,
    38782974229616694079800,
    947763561432218916176400,
    23260169594331647559707160,
    573055291303968526824841840,
    14167513861517398219221337200,
    351372806952476563815640528800
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120600

### Defining data

```json
{
  "b": 1,
  "c": 6,
  "equation": "7*A(x)=6+1*x+A(x)^6",
  "linear_coefficient_d": "1",
  "q": 6,
  "r": 7,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 15,
    "Delta_3": 20,
    "Delta_4": 15,
    "Delta_5": 6,
    "Delta_6": 1
  },
  "classification": "literal_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+15*T^2+20*T^3+15*T^4+6*T^5+1*T^6",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 15,
      "pass": true,
      "published_term": 15
    },
    "3": {
      "enumerated": 470,
      "pass": true,
      "published_term": 470
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "94ace0c408182379a8dd7de4fd34829a8e5e16b5c93d37aa54603ccc1f15226b",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 1,
      "first_five": [
        "root[0](l)"
      ],
      "last_five": [
        "root[0](l)"
      ]
    },
    "2": {
      "count": 15,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[0](Delta_2[10](l,l))",
        "root[0](Delta_2[11](l,l))",
        "root[0](Delta_2[12](l,l))",
        "root[0](Delta_2[13](l,l))",
        "root[0](Delta_2[14](l,l))"
      ]
    },
    "3": {
      "count": 470,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[0](Delta_3[15](l,l,l))",
        "root[0](Delta_3[16](l,l,l))",
        "root[0](Delta_3[17](l,l,l))",
        "root[0](Delta_3[18](l,l,l))",
        "root[0](Delta_3[19](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-15*u^1-20*u^2-15*u^3-6*u^4-1*u^5",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-15*u^1-20*u^2-15*u^3-6*u^4-1*u^5)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=4856069",
    "shape": [
      12,
      12
    ]
  },
  "expected_shift_count_for_first_nullvector": 6,
  "integrand": "(1)/(n*(-u**6 - 6*u**5 - 15*u**4 - 20*u**3 - 15*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 5,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-u**6 - 6*u**5 - 15*u**4 - 20*u**3 - 15*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `case.json#/objects/matrices`

```json
{
  "canonical_source": "case.json#/objects/matrices",
  "full_entries_location": "case.json#/objects/matrices",
  "matrix_shapes": {
    "G": [
      12,
      12
    ],
    "G_inverse": [
      12,
      12
    ],
    "J": [
      6,
      6
    ],
    "U": [
      6,
      6
    ],
    "V": [
      6,
      6
    ],
    "X": [
      5,
      6
    ],
    "X_full": [
      6,
      6
    ],
    "embedding_E": [
      12,
      6
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 30,
      "full_entries_location": "case.json#/objects/matrices",
      "full_object_sha256": "790a246f01ba9817a8e14767d57134bbb322fb8d3bcd5be7db161db7f6aff896",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "458616288986766910843904351159125387200000*n**5/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 3286750071071829527714647849973731941600000*n**4/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 6803925737706101853550613157576767312400000*n**3/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 1876221775081319471160599493723940993800000*n**2/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 5397829007638512641719541764912287780960000*n/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 2511550939457565443958268566531233419200000/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880)",
        "top_left": "1",
        "top_right": "2441242413876960042629701789863116239450176*n**5/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 18332202050134397713939248196325390484902880*n**4/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 42912759526406662361802246243674269939590480*n**3/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 27991842774063918979156343739122400762982920*n**2/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 10283437805766565688504303042716331166309816*n/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 7844827887590262116726661290320129056750960/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880)"
      },
      "shape": [
        5,
        6
      ]
    },
    "X_full": {
      "entry_count": 36,
      "full_entries_location": "case.json#/objects/matrices",
      "full_object_sha256": "41bf39019ef0ff6d4e0eb858b31a9f649d1a2a11d134b27d43bf0b4632d4405a",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "2441242413876960042629701789863116239450176*n**5/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 18332202050134397713939248196325390484902880*n**4/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 42912759526406662361802246243674269939590480*n**3/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) + 27991842774063918979156343739122400762982920*n**2/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 10283437805766565688504303042716331166309816*n/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880) - 7844827887590262116726661290320129056750960/(2700376034709895778212145501911349*n**5 + 40505640520648436673182182528670235*n**4 + 229531962950341141148032367662464665*n**3 + 607584607809726550097732737930053525*n**2 + 739903033510511443230127867523709626*n + 324045124165187493385457460229361880)"
      },
      "shape": [
        6,
        6
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `case.json#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-46656*n**5 - 349920*n**4 - 887760*n**3 - 845640*n**2 - 177480*n + 57456",
    "-1399680*n**5 - 12597120*n**4 - 42573600*n**3 - 67301280*n**2 - 49769856*n - 13844736",
    "-16796160*n**5 - 176359680*n**4 - 717336000*n**3 - 1409127840*n**2 - 1330745760*n - 479390400",
    "-100776960*n**5 - 1209323520*n**4 - 5633712000*n**3 - 12639110400*n**2 - 13497114240*n - 5383169280",
    "-302330880*n**5 - 4081466880*n**4 - 21163161600*n**3 - 52152076800*n**2 - 60163845120*n - 25395793920",
    "4856069*n**5 + 72841035*n**4 + 412765865*n**3 + 1092615525*n**2 + 1330562906*n + 582728280"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 5,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `case.json#/objects/rational_certificate`

```json
{
  "denominator_base": "-u**6 - 6*u**5 - 15*u**4 - 20*u**3 - 15*u**2 + u",
  "denominator_power": 4,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "7776*n**4*u**25 + 194400*n**4*u**24 + 2332800*n**4*u**23 + 17884800*n**4*u**22 + 98366400*n**4*u**21 + 412875792*n**4*u**20 + 1371867840*n**4*u**19 + 3687936480*n**4*u**18 + 8110406880*n**4*u**17 + 14611512240*n**4*u**16 + 21342464712*n**4*u**15 + 24516001080*n**4*u**14 + 20410797960*n**4*u**13 + 8890340760*n**4*u**12 - 4745508120*n**4*u**11 - 12691371348*n**4*u**10 - 10993895280*n**4*u**9 - 3203409060*n**4*u**8 + 3176963640*n**4*u**7 + 3971131920*n**4*u**6 + 1230354762*n**4*u**5 - 802016790*n**4*u**4 - 728148180*n**4*u**3 - 26086080*n**4*u**2 + 156648810*n**4*u - 4856069*n**4 + 59616*n**3*u**25 + 1490400*n**3*u**24 + 17884800*n**3*u**23 + 137116800*n**3*u**22 + 754142400*n**3*u**21 + 3165411312*n**3*u**20 + 10518336000*n**3*u**19 + 28281402720*n**3*u**18 + 62227556640*n**3*u**17 + 112243456080*n**3*u**16 + 164394857772*n**3*u**15 + 190016242740*n**3*u**14 + 160811009100*n**3*u**13 + 75284015220*n**3*u**12 - 27407530980*n**3*u**11 - 89260172958*n**3*u**10 - 80434717680*n**3*u**9 - 26023904910*n**3*u**8 + 19914889140*n**3*u**7 + 26956946520*n**3*u**6 + 8914067922*n**3*u**5 - 4879111710*n**3*u**4 - 4674258960*n**3*u**3 - 227215050*n**3*u**2 + 945376230*n**3*u - 29136414*n**3 + 157896*n**2*u**25 + 3947400*n**2*u**24 + 47368800*n**2*u**23 + 363160800*n**2*u**22 + 1997384400*n**2*u**21 + 8383884012*n**2*u**20 + 27861407280*n**2*u**19 + 74937884040*n**2*u**18 + 165036224520*n**2*u**17 + 298335816900*n**2*u**16 + 439107496932*n**2*u**15 + 513288823500*n**2*u**14 + 447209702820*n**2*u**13 + 234918144420*n**2*u**12 - 26937513900*n**2*u**11 - 193817435658*n**2*u**10 - 189504742440*n**2*u**9 - 70928307450*n**2*u**8 + 34977421980*n**2*u**7 + 55655350680*n**2*u**6 + 19818338352*n**2*u**5 - 8790954540*n**2*u**4 - 8975484060*n**2*u**3 - 497288370*n**2*u**2 + 1739587020*n**2*u - 53416759*n**2 + 167256*n*u**25 + 4181400*n*u**24 + 50176800*n*u**23 + 384688800*n*u**22 + 2115788400*n*u**21 + 8881125372*n*u**20 + 29518978320*n*u**19 + 79446155400*n*u**18 + 175271641560*n*u**17 + 318181557060*n*u**16 + 472808909712*n*u**15 + 564698393280*n*u**14 + 518739024240*n*u**13 + 324860717400*n*u**12 + 71061459120*n*u**11 - 108516271008*n*u**10 - 139857010920*n*u**9 - 65343084480*n*u**8 + 12194741520*n*u**7 + 32346050880*n*u**6 + 12374781912*n*u**5 - 4732772580*n*u**4 - 5028940560*n*u**3 - 296159400*n*u**2 + 950859600*n*u - 29136414*n + 57456*u**25 + 1436400*u**24 + 17236800*u**23 + 132148800*u**22 + 726818400*u**21 + 3051028512*u**20 + 10144661184*u**19 + 27339633216*u**18 + 60544777104*u**17 + 110922887376*u**16 + 168229214496*u**15 + 210007310688*u**14 + 212870917728*u**13 + 170826225696*u**12 + 103604084640*u**11 + 43175081376*u**10 + 9415716912*u**9 - 474529104*u**8 - 499292640*u**7 + 69521760*u**6 - 3389904*u**5 + 57456*u**4"
}
```

### Scalar linear ODE

Canonical source: `case.json#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "57456*x**5",
      "-2307456*x**6 - 13844736*x**5",
      "-6658200*x**7 - 79898400*x**6 - 239695200*x**5",
      "-4153680*x**8 - 74766240*x**7 - 448597440*x**6 - 897194880*x**5",
      "-816480*x**9 - 19595520*x**8 - 176359680*x**7 - 705438720*x**6 - 1058158080*x**5",
      "-46656*x**10 - 1399680*x**9 - 16796160*x**8 - 100776960*x**7 - 302330880*x**6 + 4856069*x**5"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 5
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-46656*theta**5 - 349920*theta**4 - 887760*theta**3 - 845640*theta**2 - 177480*theta + 57456",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-1399680*theta**5 - 5598720*theta**4 - 6181920*theta**3 - 1166400*theta**2 + 501984*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-16796160*theta**5 - 8398080*theta**4 + 21695040*theta**3 + 5948640*theta**2 - 2449440*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-100776960*theta**5 + 302330880*theta**4 - 191756160*theta**3 - 29393280*theta**2 + 19595520*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-302330880*theta**5 + 1965150720*theta**4 - 4232632320*theta**3 + 3476805120*theta**2 - 906992640*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "4856069*theta**5 - 48560690*theta**4 + 169962415*theta**3 - 242803450*theta**2 + 116545656*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      19
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        19
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    15,
    470,
    18390,
    805806
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    15,
    470,
    18390,
    805806,
    37828981,
    1860433080,
    94614523740,
    4935081398830,
    262560448214031,
    14193030016877406,
    777315341935068820,
    43039297954660894560,
    2405249540028525971070,
    135492504636185052358656,
    7685561884110284691089331,
    438601892971571496262327410,
    25164821367929258310475059330,
    1450741562134311371909163638910,
    83993060805236022887971639054236,
    4881690419881669201114345438559786,
    284716626699599705000488974817300650,
    16658457542119275201074344000552693200
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120601

### Defining data

```json
{
  "b": 27,
  "c": 14,
  "equation": "15*A(x)=14+27*x+A(x)^6",
  "linear_coefficient_d": "3",
  "q": 6,
  "r": 15,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 5,
    "Delta_3": 20,
    "Delta_4": 45,
    "Delta_5": 54,
    "Delta_6": 27
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(3)*T(x)",
  "recursive_equation": "T=x+5*T^2+20*T^3+45*T^4+54*T^5+27*T^6",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 15,
      "pass": true,
      "published_term": 15
    },
    "3": {
      "enumerated": 210,
      "pass": true,
      "published_term": 210
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "133d50419a79988b8f37cfe1af0a3ef6d4923c879b7753f98f6bb3699836f7e3",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 3,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ]
    },
    "2": {
      "count": 15,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[2](Delta_2[0](l,l))",
        "root[2](Delta_2[1](l,l))",
        "root[2](Delta_2[2](l,l))",
        "root[2](Delta_2[3](l,l))",
        "root[2](Delta_2[4](l,l))"
      ]
    },
    "3": {
      "count": 210,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[2](Delta_3[15](l,l,l))",
        "root[2](Delta_3[16](l,l,l))",
        "root[2](Delta_3[17](l,l,l))",
        "root[2](Delta_3[18](l,l,l))",
        "root[2](Delta_3[19](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-5*u^1-20*u^2-45*u^3-54*u^4-27*u^5",
  "coefficient_integral": "a(n)=(3)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(3)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-5*u^1-20*u^2-45*u^3-54*u^4-27*u^5)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=283580637687",
    "shape": [
      12,
      12
    ]
  },
  "expected_shift_count_for_first_nullvector": 6,
  "integrand": "(3)/(n*(-27*u**6 - 54*u**5 - 45*u**4 - 20*u**3 - 5*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 5,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-27*u**6 - 54*u**5 - 45*u**4 - 20*u**3 - 5*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      12,
      12
    ],
    "G_inverse": [
      12,
      12
    ],
    "J": [
      6,
      6
    ],
    "U": [
      6,
      6
    ],
    "V": [
      6,
      6
    ],
    "X": [
      5,
      6
    ],
    "X_full": [
      6,
      6
    ],
    "embedding_E": [
      12,
      6
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 30,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "9f9035a5c7fe27ef198748f5e8e78248d8229ec562030fb1d609ee95643b6d07",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "166884723236715426632102889000000000*n**5/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920) + 1196007183196460557530070704500000000*n**4/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920) + 2486021377537297267953612181750000000*n**3/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920) + 714900676715646384076248002875000000*n**2/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920) - 1959677877119966532346359717700000000*n/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920) - 945909067199898128750214729000000000/(1602299977273238705191803141*n**5 + 24034499659098580577877047115*n**4 + 136195498068225289941303266985*n**3 + 360517494886478708668155706725*n**2 + 439030193772867405222554060634*n + 192275997272788644623016376920)",
        "top_left": "1",
        "top_right": "414879918121602821397924380719106624*n**5/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 3126504661869489063575159136922922720*n**4/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 7414678128318279090994297734600749520*n**3/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 5147073514601666178002324882661284680*n**2/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) - 1303323116829734262704280169205537144*n/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) - 1188854062632923911917759223575060720/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840)"
      },
      "shape": [
        5,
        6
      ]
    },
    "X_full": {
      "entry_count": 36,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "431ba8f5f5688e477741b27b475eeedbb96eb20ee318dc6dda39c58d1ade1464",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "414879918121602821397924380719106624*n**5/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 3126504661869489063575159136922922720*n**4/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 7414678128318279090994297734600749520*n**3/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) + 5147073514601666178002324882661284680*n**2/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) - 1303323116829734262704280169205537144*n/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840) - 1188854062632923911917759223575060720/(43262099386377445040178684807*n**5 + 648931490795661675602680272105*n**4 + 3677278447842082828415188208595*n**3 + 9733972361934925134040204081575*n**2 + 11853815231867419941008959637118*n + 5191451926365293404821442176840)"
      },
      "shape": [
        6,
        6
      ]
    }
  },
  "statistics": {
    "G_nonzero": 72,
    "G_shape": [
      12,
      12
    ],
    "X_rank": 5,
    "X_shape": [
      5,
      6
    ],
    "certificate_degree_n": 4,
    "certificate_degree_u": 25,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 6,
    "nullity": 1,
    "recurrence_degree": 5,
    "recurrence_order": 5
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-34012224*n**5 - 255091680*n**4 - 647177040*n**3 - 616471560*n**2 - 129382920*n + 41885424",
    "-88179840*n**5 - 793618560*n**4 - 2682136800*n**3 - 4239980640*n**2 - 3135500928*n - 872218368",
    "-91445760*n**5 - 960180480*n**4 - 3905496000*n**3 - 7671918240*n**2 - 7245171360*n - 2610014400",
    "-47416320*n**5 - 568995840*n**4 - 2650704000*n**3 - 5946796800*n**2 - 6350494080*n - 2532821760",
    "-12293120*n**5 - 165957120*n**4 - 860518400*n**3 - 2120563200*n**2 - 2446330880*n - 1032622080",
    "533607*n**5 + 8004105*n**4 + 45356595*n**3 + 120061575*n**2 + 146208318*n + 64032840"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 5,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-27*u**6 - 54*u**5 - 45*u**4 - 20*u**3 - 5*u**2 + u",
  "denominator_power": 4,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "3012581722464*n**4*u**25 + 25104847687200*n**4*u**24 + 100419390748800*n**4*u**23 + 256627331913600*n**4*u**22 + 470483441841600*n**4*u**21 + 657778003043760*n**4*u**20 + 725871028190400*n**4*u**19 + 643186886493600*n**4*u**18 + 458671421599200*n**4*u**17 + 258925070221200*n**4*u**16 + 109525589768520*n**4*u**15 + 28541889210600*n**4*u**14 - 1148940012600*n**4*u**13 - 5652158470200*n**4*u**12 - 3083684434200*n**4*u**11 - 827666869500*n**4*u**10 - 4605822000*n**4*u**9 + 92732080500*n**4*u**8 + 36885699000*n**4*u**7 + 4457430000*n**4*u**6 - 1622990790*n**4*u**5 - 751039650*n**4*u**4 - 72158100*n**4*u**3 + 23504800*n**4*u**2 + 6957050*n**4*u - 533607*n**4 + 23096459872224*n**3*u**25 + 192470498935200*n**3*u**24 + 769881995740800*n**3*u**23 + 1967476211337600*n**3*u**22 + 3607039720785600*n**3*u**21 + 5043068002132560*n**3*u**20 + 5565796388317440*n**3*u**19 + 4933891186463520*n**3*u**18 + 3522675035100960*n**3*u**17 + 1994732374708080*n**3*u**16 + 850873423450860*n**3*u**15 + 228765230143740*n**3*u**14 - 1986740215380*n**3*u**13 - 39817811061540*n**3*u**12 - 22409176987620*n**3*u**11 - 6175516821210*n**3*u**10 - 141981847920*n**3*u**9 + 626460835590*n**3*u**8 + 255648508020*n**3*u**7 + 32330606760*n**3*u**6 - 10336094910*n**3*u**5 - 4904150730*n**3*u**4 - 478599440*n**3*u**3 + 144674530*n**3*u**2 + 42552790*n**3*u - 3201642*n**3 + 61172145531144*n**2*u**25 + 509767879426200*n**2*u**24 + 2039071517704800*n**2*u**23 + 5210960545245600*n**2*u**22 + 9553427666283600*n**2*u**21 + 13357270968940260*n**2*u**20 + 14744823189856560*n**2*u**19 + 13080521590784280*n**2*u**18 + 9359074399431240*n**2*u**17 + 5329135921874220*n**2*u**16 + 2307607687782180*n**2*u**15 + 654561798875460*n**2*u**14 + 28596948466500*n**2*u**13 - 87637945621140*n**2*u**12 - 52802829191340*n**2*u**11 - 15196519579230*n**2*u**10 - 738819328680*n**2*u**9 + 1300195499490*n**2*u**8 + 552603972060*n**2*u**7 + 72995553000*n**2*u**6 - 20085457680*n**2*u**5 - 9720966420*n**2*u**4 - 939263580*n**2*u**3 + 272578250*n**2*u**2 + 78959020*n**2*u - 5869677*n**2 + 64798401308184*n*u**25 + 539986677568200*n*u**24 + 2159946710272800*n*u**23 + 5519863815141600*n*u**22 + 10119750327759600*n*u**21 + 14149933289434260*n*u**20 + 15625776439627920*n*u**19 + 13881610482289560*n*u**18 + 9972984541357080*n*u**17 + 5739754051444140*n*u**16 + 2556921455018640*n*u**15 + 795784647381120*n*u**14 + 102432269332080*n*u**13 - 54104128702200*n*u**12 - 41034976157520*n*u**11 - 12875420668320*n*u**10 - 1120368312360*n*u**9 + 791643585600*n*u**8 + 363280807440*n*u**7 + 48612666240*n*u**6 - 11939904360*n*u**5 - 5656890540*n*u**4 - 523847440*n*u**3 + 151408520*n*u**2 + 43363280*n*u - 3201642*n + 22259631615984*u**25 + 185496930133200*u**24 + 741987720532800*u**23 + 1896190841361600*u**22 + 3476349875829600*u**21 + 4861393620824160*u**20 + 5372723924035776*u**19 + 4787439124563648*u**18 + 3469907101795344*u**17 + 2043026603663472*u**16 + 963881366819616*u**15 + 351925269677856*u**14 + 91148462812512*u**13 + 12063644355168*u**12 - 1723864433760*u**11 - 1224087554592*u**10 - 209999554128*u**9 + 14925172752*u**8 + 10192119840*u**7 + 139618080*u**6 - 237350736*u**5 + 13961808*u**4"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "41885424*x**5",
      "-1682135424*x**6 - 872218368*x**5",
      "-4853827800*x**7 - 5033599200*x**6 - 1305007200*x**5",
      "-3028032720*x**8 - 4710273120*x**7 - 2442363840*x**6 - 422136960*x**5",
      "-595213920*x**9 - 1234517760*x**8 - 960180480*x**7 - 331914240*x**6 - 43025920*x**5",
      "-34012224*x**10 - 88179840*x**9 - 91445760*x**8 - 47416320*x**7 - 12293120*x**6 + 533607*x**5"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 5
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-34012224*theta**5 - 255091680*theta**4 - 647177040*theta**3 - 616471560*theta**2 - 129382920*theta + 41885424",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-88179840*theta**5 - 352719360*theta**4 - 389460960*theta**3 - 73483200*theta**2 + 31624992*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-91445760*theta**5 - 45722880*theta**4 + 118117440*theta**3 + 32387040*theta**2 - 13335840*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-47416320*theta**5 + 142248960*theta**4 - 90222720*theta**3 - 13829760*theta**2 + 9219840*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-12293120*theta**5 + 79905280*theta**4 - 172103680*theta**3 + 141370880*theta**2 - 36879360*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "533607*theta**5 - 5336070*theta**4 + 18676245*theta**3 - 26680350*theta**2 + 12806568*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      18
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        18
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    15,
    210,
    3510,
    65562
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    15,
    210,
    3510,
    65562,
    1310901,
    27446760,
    594104940,
    13187589690,
    298555767279,
    6867021319722,
    160017552201780,
    3769622456958720,
    89628027015591870,
    2148034269252052608,
    51836638064282565579,
    1258523552872075947030,
    30719188200563825288370,
    753402668745477409444170,
    18556605112417664324218956,
    458818224826837085103821598,
    11384035695214779795515534250,
    283353908259305331549813942000
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120602

### Defining data

```json
{
  "b": 125,
  "c": 30,
  "equation": "31*A(x)=30+125*x+A(x)^6",
  "linear_coefficient_d": "5",
  "q": 6,
  "r": 31,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_3": 20,
    "Delta_4": 75,
    "Delta_5": 150,
    "Delta_6": 125
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(5)*T(x)",
  "recursive_equation": "T=x+3*T^2+20*T^3+75*T^4+150*T^5+125*T^6",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 5,
      "pass": true,
      "published_term": 5
    },
    "2": {
      "enumerated": 15,
      "pass": true,
      "published_term": 15
    },
    "3": {
      "enumerated": 190,
      "pass": true,
      "published_term": 190
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "8d8772dd033fea81238f91371e9bf316bbb5ce9e49a5dd43d62d228847eb1c00",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 5,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)",
        "root[4](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)",
        "root[4](l)"
      ]
    },
    "2": {
      "count": 15,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[1](Delta_2[0](l,l))",
        "root[1](Delta_2[1](l,l))"
      ],
      "last_five": [
        "root[3](Delta_2[1](l,l))",
        "root[3](Delta_2[2](l,l))",
        "root[4](Delta_2[0](l,l))",
        "root[4](Delta_2[1](l,l))",
        "root[4](Delta_2[2](l,l))"
      ]
    },
    "3": {
      "count": 190,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[1](l,l)))"
      ],
      "last_five": [
        "root[4](Delta_3[15](l,l,l))",
        "root[4](Delta_3[16](l,l,l))",
        "root[4](Delta_3[17](l,l,l))",
        "root[4](Delta_3[18](l,l,l))",
        "root[4](Delta_3[19](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-3*u^1-20*u^2-75*u^3-150*u^4-125*u^5",
  "coefficient_integral": "a(n)=(5)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(5)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-20*u^2-75*u^3-150*u^4-125*u^5)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=204963525390625",
    "shape": [
      12,
      12
    ]
  },
  "expected_shift_count_for_first_nullvector": 6,
  "integrand": "(5)/(n*(-125*u**6 - 150*u**5 - 75*u**4 - 20*u**3 - 3*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 5,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-125*u**6 - 150*u**5 - 75*u**4 - 20*u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      12,
      12
    ],
    "G_inverse": [
      12,
      12
    ],
    "J": [
      6,
      6
    ],
    "U": [
      6,
      6
    ],
    "V": [
      6,
      6
    ],
    "X": [
      5,
      6
    ],
    "X_full": [
      6,
      6
    ],
    "embedding_E": [
      12,
      6
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 30,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "6aa516e44497af74a7fe717be5936f8fe5bb0dce37474269c40b25d4b42f7c16",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "190497189186410592125019482695328720832000*n**5/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 1365229855835942576895972959316522499296000*n**4/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 2855873291158139971747848236807176520208000*n**3/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 873385974672500070506239380956404953864000*n**2/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 2228033772330852593601375839857173540960000*n/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 1137470538108477779168297165815619620800000/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160)",
        "top_left": "1",
        "top_right": "3266825924293884742738802154817700471616*n**5/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 24643052915402323391154349004558288822880*n**4/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 58988634654185827789699431911107553164560*n**3/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 42912163113237712332484851265239808662120*n**2/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 7224418077368174782998972186514399724376*n/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 8256674187509480791892607324802943755440/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160)"
      },
      "shape": [
        5,
        6
      ]
    },
    "X_full": {
      "entry_count": 36,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "6682d12488bde84e9825d921814376a3d0b0d92695ec1d94083dd8c8b064405e",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "3266825924293884742738802154817700471616*n**5/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 24643052915402323391154349004558288822880*n**4/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 58988634654185827789699431911107553164560*n**3/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) + 42912163113237712332484851265239808662120*n**2/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 7224418077368174782998972186514399724376*n/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160) - 8256674187509480791892607324802943755440/(1303264823534156225932725788623493*n**5 + 19548972353012343388990886829352395*n**4 + 110777510000403279204281692032996905*n**3 + 293234585295185150834863302440285925*n**2 + 357094561648358805905566866082837082*n + 156391778824098747111927094634819160)"
      },
      "shape": [
        6,
        6
      ]
    }
  },
  "statistics": {
    "G_nonzero": 72,
    "G_shape": [
      12,
      12
    ],
    "X_rank": 5,
    "X_shape": [
      5,
      6
    ],
    "certificate_degree_n": 4,
    "certificate_degree_u": 25,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 6,
    "nullity": 1,
    "recurrence_degree": 5,
    "recurrence_order": 5
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-3645000000*n**5 - 27337500000*n**4 - 69356250000*n**3 - 66065625000*n**2 - 13865625000*n + 4488750000",
    "-4374000000*n**5 - 39366000000*n**4 - 133042500000*n**3 - 210316500000*n**2 - 155530800000*n - 43264800000",
    "-2099520000*n**5 - 22044960000*n**4 - 89667000000*n**3 - 176140980000*n**2 - 166343220000*n - 59923800000",
    "-503884800*n**5 - 6046617600*n**4 - 28168560000*n**3 - 63195552000*n**2 - 67485571200*n - 26915846400",
    "-60466176*n**5 - 816293376*n**4 - 4232632320*n**3 - 10430415360*n**2 - 12032769024*n - 5079158784",
    "4197653*n**5 + 62964795*n**4 + 356800505*n**3 + 944471925*n**2 + 1150156922*n + 503718360"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 5,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-125*u**6 - 150*u**5 - 75*u**4 - 20*u**3 - 3*u**2 + u",
  "denominator_power": 4,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "148315429687500000*n**4*u**25 + 741577148437500000*n**4*u**24 + 1779785156250000000*n**4*u**23 + 2729003906250000000*n**4*u**22 + 3001904296875000000*n**4*u**21 + 2514488378906250000*n**4*u**20 + 1652621484375000000*n**4*u**19 + 858533554687500000*n**4*u**18 + 345806085937500000*n**4*u**17 + 100012155468750000*n**4*u**16 + 14497681640625000*n**4*u**15 - 3698466328125000*n**4*u**14 - 3333361359375000*n**4*u**13 - 1172947415625000*n**4*u**12 - 210138046875000*n**4*u**11 + 9078409687500*n**4*u**10 + 18057692250000*n**4*u**9 + 5387645137500*n**4*u**8 + 600828975000*n**4*u**7 - 111827790000*n**4*u**6 - 55972506750*n**4*u**5 - 7793161350*n**4*u**4 + 418259100*n**4*u**3 + 282308640*n**4*u**2 + 35280258*n**4*u - 4197653*n**4 + 1137084960937500000*n**3*u**25 + 5685424804687500000*n**3*u**24 + 13645019531250000000*n**3*u**23 + 20922363281250000000*n**3*u**22 + 23014599609375000000*n**3*u**21 + 19278561621093750000*n**3*u**20 + 12673842187500000000*n**3*u**19 + 6590106210937500000*n**3*u**18 + 2661880851562500000*n**3*u**17 + 776775382031250000*n**3*u**16 + 118111344960937500*n**3*u**15 - 24686202304687500*n**3*u**14 - 24118553039062500*n**3*u**13 - 8614465467187500*n**3*u**12 - 1575872035312500*n**3*u**11 + 46983982031250*n**3*u**10 + 125006909250000*n**3*u**9 + 37753700231250*n**3*u**8 + 4297361602500*n**3*u**7 - 726709005000*n**3*u**6 - 372036465750*n**3*u**5 - 51531779550*n**3*u**4 + 2601639600*n**3*u**3 + 1769725830*n**3*u**2 + 216728718*n**3*u - 25185918*n**3 + 3011627197265625000*n**2*u**25 + 15058135986328125000*n**2*u**24 + 36139526367187500000*n**2*u**23 + 55413940429687500000*n**2*u**22 + 60955334472656250000*n**2*u**21 + 51063805151367187500*n**2*u**20 + 33584160058593750000*n**2*u**19 + 17491214267578125000*n**2*u**18 + 7100478087890625000*n**2*u**17 + 2105203410351562500*n**2*u**16 + 346562142070312500*n**2*u**15 - 47350107070312500*n**2*u**14 - 56670840492187500*n**2*u**13 - 20833306598437500*n**2*u**12 - 3932615685937500*n**2*u**11 + 40940504343750*n**2*u**10 + 273042343875000*n**2*u**9 + 83760113643750*n**2*u**8 + 9670955287500*n**2*u**7 - 1474165365000*n**2*u**6 - 763651266000*n**2*u**5 - 103066071900*n**2*u**4 + 5196894900*n**2*u**3 + 3375043710*n**2*u**2 + 403224348*n**2*u - 46174183*n**2 + 3190155029296875000*n*u**25 + 15950775146484375000*n*u**24 + 38281860351562500000*n*u**23 + 58698852539062500000*n*u**22 + 64568737792968750000*n*u**21 + 54097565405273437500*n*u**20 + 35607920800781250000*n*u**19 + 18602046298828125000*n*u**18 + 7623868341796875000*n*u**17 + 2328769879101562500*n*u**16 + 437521893281250000*n*u**15 - 12061192500000000*n*u**14 - 44523274781250000*n*u**13 - 17621811440625000*n*u**12 - 3500665616250000*n*u**11 - 63124225500000*n*u**10 + 189627595875000*n*u**9 + 59169619800000*n*u**8 + 6696240210000*n*u**7 - 970815840000*n*u**6 - 475736517000*n*u**5 - 59252933700*n*u**4 + 3279284400*n*u**3 + 1887626520*n*u**2 + 221775888*n*u - 25185918*n + 1095886230468750000*u**25 + 5479431152343750000*u**24 + 13150634765625000000*u**23 + 20164306640625000000*u**22 + 22180737304687500000*u**21 + 18588334570312500000*u**20 + 12255690234375000000*u**19 + 6444442265625000000*u**18 + 2695312019531250000*u**17 + 874450582031250000*u**16 + 203918301562500000*u**15 + 25178520937500000*u**14 - 3149980312500000*u**13 - 2419660687500000*u**12 - 551263387500000*u**11 - 35416237500000*u**10 + 13165503750000*u**9 + 3573942750000*u**8 + 163390500000*u**7 - 77206500000*u**6 - 6284250000*u**5 + 897750000*u**4"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "4488750000*x**5",
      "-180270000000*x**6 - 43264800000*x**5",
      "-520171875000*x**7 - 249682500000*x**6 - 29961900000*x**5",
      "-324506250000*x**8 - 233644500000*x**7 - 56074680000*x**6 - 4485974400*x**5",
      "-63787500000*x**9 - 61236000000*x**8 - 22044960000*x**7 - 3527193600*x**6 - 211631616*x**5",
      "-3645000000*x**10 - 4374000000*x**9 - 2099520000*x**8 - 503884800*x**7 - 60466176*x**6 + 4197653*x**5"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 5
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-3645000000*theta**5 - 27337500000*theta**4 - 69356250000*theta**3 - 66065625000*theta**2 - 13865625000*theta + 4488750000",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-4374000000*theta**5 - 17496000000*theta**4 - 19318500000*theta**3 - 3645000000*theta**2 + 1568700000*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-2099520000*theta**5 - 1049760000*theta**4 + 2711880000*theta**3 + 743580000*theta**2 - 306180000*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-503884800*theta**5 + 1511654400*theta**4 - 958780800*theta**3 - 146966400*theta**2 + 97977600*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-60466176*theta**5 + 393030144*theta**4 - 846526464*theta**3 + 695361024*theta**2 - 181398528*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "4197653*theta**5 - 41976530*theta**4 + 146917855*theta**3 - 209882650*theta**2 + 100743672*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      18
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        18
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    5,
    15,
    190,
    2550,
    38070
  ],
  "status": "verified",
  "terms": [
    1,
    5,
    15,
    190,
    2550,
    38070,
    609205,
    10199640,
    176483340,
    3130904150,
    56641633455,
    1040985874470,
    19381240377460,
    364777461207360,
    6929053224018750,
    132665646902812800,
    2557591625106894075,
    49604907701733017850,
    967242234362414552850,
    18950004748051829487750,
    372848735641925952297900,
    7364153452990151479236850,
    145956370321191907669819050,
    2902002178259957385049030800
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120603

### Defining data

```json
{
  "b": 27,
  "c": 15,
  "equation": "16*A(x)=15+27*x+A(x)^7",
  "linear_coefficient_d": "3",
  "q": 7,
  "r": 16,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 7,
    "Delta_3": 35,
    "Delta_4": 105,
    "Delta_5": 189,
    "Delta_6": 189,
    "Delta_7": 81
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(3)*T(x)",
  "recursive_equation": "T=x+7*T^2+35*T^3+105*T^4+189*T^5+189*T^6+81*T^7",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6",
      "Delta_7"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "Delta_7": 6,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 21,
      "pass": true,
      "published_term": 21
    },
    "3": {
      "enumerated": 399,
      "pass": true,
      "published_term": 399
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "227e06b95c5736d64804ab0a04039014d9b0985c76632590b935860cc031097b",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 3,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ]
    },
    "2": {
      "count": 21,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[2](Delta_2[2](l,l))",
        "root[2](Delta_2[3](l,l))",
        "root[2](Delta_2[4](l,l))",
        "root[2](Delta_2[5](l,l))",
        "root[2](Delta_2[6](l,l))"
      ]
    },
    "3": {
      "count": 399,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[2](Delta_3[30](l,l,l))",
        "root[2](Delta_3[31](l,l,l))",
        "root[2](Delta_3[32](l,l,l))",
        "root[2](Delta_3[33](l,l,l))",
        "root[2](Delta_3[34](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-7*u^1-35*u^2-105*u^3-189*u^4-189*u^5-81*u^6",
  "coefficient_integral": "a(n)=(3)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(3)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-7*u^1-35*u^2-105*u^3-189*u^4-189*u^5-81*u^6)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=185617883197286289",
    "shape": [
      14,
      14
    ]
  },
  "expected_shift_count_for_first_nullvector": 7,
  "integrand": "(3)/(n*(-81*u**7 - 189*u**6 - 189*u**5 - 105*u**4 - 35*u**3 - 7*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 6,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-81*u**7 - 189*u**6 - 189*u**5 - 105*u**4 - 35*u**3 - 7*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      14,
      14
    ],
    "G_inverse": [
      14,
      14
    ],
    "J": [
      7,
      7
    ],
    "U": [
      7,
      7
    ],
    "V": [
      7,
      7
    ],
    "X": [
      6,
      7
    ],
    "X_full": [
      7,
      7
    ],
    "embedding_E": [
      14,
      7
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 42,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "f27b0e8ba7e7f0fce93aa0de7326ef9b81bb90bff3ad9223cb80f44eed00f819",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "9812440441030347628135897305199799511977926772879985213440*n**6/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) + 114244842277710475956153661481969094318028718855674113556480*n**5/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) + 459804562562240092132795855265495343155013564873655818649600*n**4/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) + 686413814261740597684042148059818468730978189327941710643200*n**3/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) + 45273198387158923710940573904338351102623175912971420303360*n**2/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) - 599531260281448925818147387803866217349874016033404595732480*n/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280) - 256577981236933394170161138214278941571257011953401541427200/(204838146240212883341563885760110975400913930249*n**6 + 4301601071044470550172841600962330483419192535229*n**5 + 35846675592037254584773680008019420695159937793575*n**4 + 150556037486556469256049456033681566919671738733015*n**3 + 332657149494105722546699750474420224051084222724376*n**2 + 361334489967735526214518694480835760607212172959236*n + 147483465292953276005925997747279902288658029779280)",
        "top_left": "1",
        "top_right": "28467731507955055015789289356808082102085196849486667626113*n**6/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 342638003350004518867216139201586777094781468093337013292581*n**5/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 1474408079317427471432206244495681818222791775789946420899575*n**4/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 2642121426515578836409526394653425933114573003594072699749215*n**3/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 1493925001887576899822015493368258223726246369728730326471552*n**2/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) - 493393085615889005253760653879997308157108367718457785230556*n/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) - 370825030220841929866694102517489453645333992236849318932240/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680)"
      },
      "shape": [
        6,
        7
      ]
    },
    "X_full": {
      "entry_count": 49,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "61757b93074d2e21fd407a7a4e1e865acdfbf1de52e4614054bc7503cfb10019",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "28467731507955055015789289356808082102085196849486667626113*n**6/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 342638003350004518867216139201586777094781468093337013292581*n**5/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 1474408079317427471432206244495681818222791775789946420899575*n**4/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 2642121426515578836409526394653425933114573003594072699749215*n**3/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) + 1493925001887576899822015493368258223726246369728730326471552*n**2/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) - 493393085615889005253760653879997308157108367718457785230556*n/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680) - 370825030220841929866694102517489453645333992236849318932240/(16591889845457243550666674746568989007474028350169*n**6 + 348429686754602114564000169677948769156954595353549*n**5 + 2903580722955017621366668080649573076307954961279575*n**4 + 12195039036411074009740005938728206920493410837374215*n**3 + 26945229109022563526282679788428038148137822040674456*n**2 + 29268093687386577623376014252947696609184186009698116*n + 11946160688729215356480005817529672085381300412121680)"
      },
      "shape": [
        7,
        7
      ]
    }
  },
  "statistics": {
    "G_nonzero": 98,
    "G_shape": [
      14,
      14
    ],
    "X_rank": 6,
    "X_shape": [
      6,
      7
    ],
    "certificate_degree_n": 5,
    "certificate_degree_u": 36,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 7,
    "nullity": 1,
    "recurrence_degree": 6,
    "recurrence_order": 6
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-16209796869*n**6 - 194517562428*n**5 - 868381975125*n**4 - 1759920802920*n**3 - 1531046032551*n**2 - 344233703772*n + 85926431745",
    "-54032656230*n**6 - 729440859105*n**5 - 3865907904075*n**4 - 10234042388325*n**3 - 14202003224745*n**2 - 9777521578545*n - 2619061040925",
    "-75045355875*n**6 - 1125680338125*n**5 - 6786244324125*n**4 - 21001978879875*n**3 - 35094898684125*n**2 - 29896275693375*n - 10067746547250",
    "-55589152500*n**6 - 917221016250*n**5 - 6126718736250*n**4 - 21111965988750*n**3 - 39321384086250*n**2 - 37149436485000*n - 13674931515000",
    "-23162146875*n**6 - 416918643750*n**5 - 3032035321875*n**4 - 11327392781250*n**3 - 22714345368750*n**2 - 22866553762500*n - 8841322350000",
    "-5147143750*n**6 - 100369303125*n**5 - 784939421875*n**4 - 3126889828125*n**3 - 6621800434375*n**2 - 6964085493750*n - 2779457625000",
    "159704067*n**6 + 3353785407*n**5 + 27948211725*n**4 + 117382489245*n**3 + 259359404808*n**2 + 281717974188*n + 114986928240"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 6,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-81*u**7 - 189*u**6 - 189*u**5 - 105*u**4 - 35*u**3 - 7*u**2 + u",
  "denominator_power": 5,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "numerator_N": "-8074295266601120067*n**5*u**36 - 96891543199213440804*n**5*u**35 - 565200668662078404690*n**5*u**34 - 2135202526056740639940*n**5*u**33 - 5871806946656036759835*n**5*u**32 - 12526521486199545087648*n**5*u**31 - 21572415705226300542432*n**5*u**30 - 30808839875031625559040*n**5*u**29 - 37189721934742231533420*n**5*u**28 - 38463066210601407337200*n**5*u**27 - 34406052603050430241128*n**5*u**26 - 26775775890357202891728*n**5*u**25 - 18171629266838511653532*n**5*u**24 - 10737007175006562121056*n**5*u**23 - 5484403511649963690048*n**5*u**22 - 2382777637600293831744*n**5*u**21 - 849835578858323983002*n**5*u**20 - 227100930232979249496*n**5*u**19 - 30374511241407450012*n**5*u**18 + 9532299202537821192*n**5*u**17 + 8486773510942415430*n**5*u**16 + 3310014627246755232*n**5*u**15 + 758023172473889952*n**5*u**14 + 42264982307140992*n**5*u**13 - 45302989256949564*n**5*u**12 - 20950308189039600*n**5*u**11 - 4388102632516680*n**5*u**10 - 98825095054224*n**5*u**9 + 236576541124980*n**5*u**8 + 73594288109664*n**5*u**7 + 7223840636544*n**5*u**6 - 1685605352256*n**5*u**5 - 642973380987*n**5*u**4 - 54524322468*n**5*u**3 + 11121228958*n**5*u**2 + 2911286812*n**5*u - 159704067*n**5 - 98045013951585029385*n**4*u**36 - 1176540167419020352620*n**4*u**35 - 6863150976610952056950*n**4*u**34 - 25927459244974707770700*n**4*u**33 - 71300512923680446369425*n**4*u**32 - 152107760903851618921440*n**4*u**31 - 261950870633021526841920*n**4*u**30 - 374108544990807575244975*n**4*u**29 - 451595871854169250173525*n**4*u**28 - 467073186503600375354250*n**4*u**27 - 417840550126427798793990*n**4*u**26 - 325232846283175191036585*n**4*u**25 - 220801851823861654487379*n**4*u**24 - 130556149640600758777332*n**4*u**23 - 66777311326272814701756*n**4*u**22 - 29088901955602104608223*n**4*u**21 - 10432505965829416874559*n**4*u**20 - 2827755650119549254462*n**4*u**19 - 405583134755022875574*n**4*u**18 + 99744320741987400759*n**4*u**17 + 97504258676646845835*n**4*u**16 + 38835923172212653704*n**4*u**15 + 9093331280255826744*n**4*u**14 + 605903493254954139*n**4*u**13 - 492113749481275887*n**4*u**12 - 236259951759404118*n**4*u**11 - 50551479619925130*n**4*u**10 - 1568861719446483*n**4*u**9 + 2537672725442295*n**4*u**8 + 806352146183052*n**4*u**7 + 81554382822276*n**4*u**6 - 17380380652173*n**4*u**5 - 6773023908084*n**4*u**4 - 579766606006*n**4*u**3 + 112656605180*n**4*u**2 + 29450583057*n**4*u - 1597040670*n**4 - 446557962703857864930*n**3*u**36 - 5358695552446294379160*n**3*u**35 - 31259057389270050545100*n**3*u**34 - 118089772359464635392600*n**3*u**33 - 324746873988527747329650*n**3*u**32 - 692793331175525860969920*n**3*u**31 - 1193087904492173179855680*n**3*u**30 - 1703931407482725923569200*n**3*u**29 - 2056894105683379471752600*n**3*u**28 - 2127498843996060792062400*n**3*u**27 - 1903492899383160847018320*n**3*u**26 - 1482042217867256269289520*n**3*u**25 - 1006763340677343751352088*n**3*u**24 - 595976701540196893984704*n**3*u**23 - 305518485433975861363407*n**3*u**22 - 133673685411524361879006*n**3*u**21 - 48384803041471123338573*n**3*u**20 - 13421515661455171840164*n**3*u**19 - 2133829601443171830933*n**3*u**18 + 328020165295172426538*n**3*u**17 + 399384812507724732465*n**3*u**16 + 165372679393901774928*n**3*u**15 + 40086615957877722618*n**3*u**14 + 3300734401387803828*n**3*u**13 - 1842396087917723058*n**3*u**12 - 943662453297254712*n**3*u**11 - 207918583875703386*n**3*u**10 - 8630862375223116*n**3*u**9 + 9474107383991250*n**3*u**8 + 3092574061070928*n**3*u**7 + 321192133897509*n**3*u**6 - 62501717841318*n**3*u**5 - 24801475899543*n**3*u**4 - 2123464424172*n**3*u**3 + 399511308539*n**3*u**2 + 103921328042*n**3*u - 5589642345*n**3 - 940431766474387016550*n**2*u**36 - 11285181197692644198600*n**2*u**35 - 65830223653207091158500*n**2*u**34 - 248691956023226788821000*n**2*u**33 - 683902879063873669257750*n**2*u**32 - 1458992808669597161083200*n**2*u**31 - 2512594057838381003491200*n**2*u**30 - 3588434883765941503472325*n**2*u**29 - 4331889344352342129671475*n**2*u**28 - 4480975627619218759763550*n**2*u**27 - 4010056495545050830211850*n**2*u**26 - 3123745711838477490021075*n**2*u**25 - 2124173397540523703914701*n**2*u**24 - 1260008248914930225243708*n**2*u**23 - 648455435449684038297639*n**2*u**22 - 285888675025739462956587*n**2*u**21 - 105123139659326171117196*n**2*u**20 - 30290915054731970350278*n**2*u**19 - 5572614138314506056711*n**2*u**18 + 209815533613967675751*n**2*u**17 + 667104139814427229320*n**2*u**16 + 301101473224376067726*n**2*u**15 + 77397989532877091736*n**2*u**14 + 8146215451142344611*n**2*u**13 - 2647549601213312565*n**2*u**12 - 1545640145515152540*n**2*u**11 - 355254751280800098*n**2*u**10 - 19065813674768847*n**2*u**9 + 14261644383823305*n**2*u**8 + 4809966127611750*n**2*u**7 + 507727247112855*n**2*u**6 - 91841475626523*n**2*u**5 - 36729511889406*n**2*u**4 - 3123372405104*n**2*u**3 + 576756123727*n**2*u**2 + 149279204907*n**2*u - 7985203350*n**2 - 896979884283736007643*n*u**36 - 10763758611404832091716*n*u**35 - 62788591899861520535010*n*u**34 - 237201347177254633132260*n*u**33 - 652303704737450241113715*n*u**32 - 1391581236773227181042592*n*u**31 - 2396505805109411055445728*n*u**30 - 3422682733092984217011960*n*u**29 - 4132008885383648901050580*n*u**28 - 4274891620671790197576000*n*u**27 - 3827179606161462116153112*n*u**26 - 2984023507068650448386712*n*u**25 - 2033038418254073749742580*n*u**24 - 1210497745056494995326240*n*u**23 - 627493338940865743457370*n*u**22 - 280521454727886135201900*n*u**21 - 106073452829394635923800*n*u**20 - 32557163838081331609440*n*u**19 - 7282233244656300857850*n*u**18 - 687727507032831559140*n*u**17 + 307486317035452404780*n*u**16 + 192994706308127408370*n*u**15 + 56510366466895387830*n*u**14 + 7971146020294371810*n*u**13 - 954948045674236950*n*u**12 - 833080928850246006*n*u**11 - 205536056241802482*n*u**10 - 13461377021518230*n*u**9 + 7169169832729065*n*u**8 + 2487396522086910*n*u**7 + 261060381339408*n*u**6 - 45470950320222*n*u**5 - 18039156504705*n*u**4 - 1525150264470*n*u**3 + 278780191410*n*u**2 + 71897173110*n*u - 3832897608*n - 299606941842057209745*u**36 - 3595283302104686516940*u**35 - 20972485928944004682150*u**34 - 79229391287121795465900*u**33 - 217880826039584937531225*u**32 - 464812428884447866733280*u**31 - 800477415513137081079360*u**30 - 1143267622376004273265425*u**29 - 1380343430882987402814675*u**28 - 1428531774244236048028950*u**27 - 1279977571266654139255530*u**26 - 999867182421476137503735*u**25 - 683892760606866347246325*u**24 - 410346169986249851993100*u**23 - 215841178272486602231550*u**22 - 99165090268460963179125*u**21 - 39495572349923422084275*u**20 - 13454535450979419107850*u**19 - 3827977989977533392000*u**18 - 868461999134299814475*u**17 - 140349369254680780425*u**16 - 9548849405823269850*u**15 + 2504080390034673450*u**14 + 942337562028907275*u**13 + 123444060005660625*u**12 - 4252670959923540*u**11 - 3712365557110980*u**10 - 303749936218575*u**9 + 54133651999350*u**8 + 6014850222150*u**7 - 916548605280*u**6 + 28642143915*u**5"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "85926431745*x**6",
      "-4714309873665*x**7 - 2619061040925*x**6",
      "-16309749406545*x**8 - 18121943785050*x**7 - 5033873273625*x**6",
      "-13292033432580*x**9 - 22153389054300*x**8 - 12307438363500*x**7 - 2279155252500*x**6",
      "-3867194395890*x**10 - 8593765324200*x**9 - 7161471103500*x**8 - 2652396705000*x**7 - 368388431250*x**6",
      "-437664515463*x**11 - 1215734765175*x**10 - 1350816405750*x**9 - 750453558750*x**8 - 208459321875*x**7 - 23162146875*x**6",
      "-16209796869*x**12 - 54032656230*x**11 - 75045355875*x**10 - 55589152500*x**9 - 23162146875*x**8 - 5147143750*x**7 + 159704067*x**6"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 6
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-16209796869*theta**6 - 194517562428*theta**5 - 868381975125*theta**4 - 1759920802920*theta**3 - 1531046032551*theta**2 - 344233703772*theta + 85926431745",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 6
      },
      {
        "polynomial_in_theta": "-54032656230*theta**6 - 405244921725*theta**5 - 1029193452000*theta**4 - 984166238475*theta**3 - 211404736620*theta**2 + 64980964125*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-75045355875*theta**6 - 225136067625*theta**5 - 32162295375*theta**4 + 268019128125*theta**3 + 90652456125*theta**2 - 26327865375*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-55589152500*theta**6 + 83383728750*theta**5 + 127060920000*theta**4 - 123090266250*theta**3 - 47647845000*theta**2 + 15882615000*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-23162146875*theta**6 + 138972881250*theta**5 - 252577696875*theta**4 + 125737368750*theta**3 + 24265106250*theta**2 - 13235512500*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-5147143750*theta**6 + 54045009375*theta**5 - 205885750000*theta**4 + 347432203125*theta**3 - 252210043750*theta**2 + 61765725000*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "159704067*theta**6 - 2395561005*theta**5 + 13574845695*theta**4 - 35933415075*theta**3 + 43758914358*theta**2 - 19164488040*theta",
        "shift": 6,
        "source": "P_6(theta-6)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      17
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        17
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    21,
    399,
    9135,
    233709
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    21,
    399,
    9135,
    233709,
    6400947,
    183585897,
    5443737390,
    165536020650,
    5133935821014,
    161768728483362,
    5164132704296202,
    166660621950110526,
    5428573285691233650,
    178234125351736454070,
    5892439158797172244515,
    195987753344902193361225,
    6553709490502628480747343,
    220198792821335474068865565,
    7430140428051408971007025845,
    251680867307202028504848534495,
    8554942945848563899801116018705,
    291716937321172568742876461073315
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120604

### Defining data

```json
{
  "b": 64,
  "c": 23,
  "equation": "24*A(x)=23+64*x+A(x)^8",
  "linear_coefficient_d": "4",
  "q": 8,
  "r": 24,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 7,
    "Delta_3": 56,
    "Delta_4": 280,
    "Delta_5": 896,
    "Delta_6": 1792,
    "Delta_7": 2048,
    "Delta_8": 1024
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(4)*T(x)",
  "recursive_equation": "T=x+7*T^2+56*T^3+280*T^4+896*T^5+1792*T^6+2048*T^7+1024*T^8",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6",
      "Delta_7",
      "Delta_8"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "Delta_7": 6,
      "Delta_8": 7,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 4,
      "pass": true,
      "published_term": 4
    },
    "2": {
      "enumerated": 28,
      "pass": true,
      "published_term": 28
    },
    "3": {
      "enumerated": 616,
      "pass": true,
      "published_term": 616
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "e7c6069c3a978ec0ed6e5339b1c9403600601592063b6dadb9749410ceaca754",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 4,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ]
    },
    "2": {
      "count": 28,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[3](Delta_2[2](l,l))",
        "root[3](Delta_2[3](l,l))",
        "root[3](Delta_2[4](l,l))",
        "root[3](Delta_2[5](l,l))",
        "root[3](Delta_2[6](l,l))"
      ]
    },
    "3": {
      "count": 616,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[3](Delta_3[51](l,l,l))",
        "root[3](Delta_3[52](l,l,l))",
        "root[3](Delta_3[53](l,l,l))",
        "root[3](Delta_3[54](l,l,l))",
        "root[3](Delta_3[55](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-7*u^1-56*u^2-280*u^3-896*u^4-1792*u^5-2048*u^6-1024*u^7",
  "coefficient_integral": "a(n)=(4)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(4)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-7*u^1-56*u^2-280*u^3-896*u^4-1792*u^5-2048*u^6-1024*u^7)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=9216178618322768326090031104",
    "shape": [
      16,
      16
    ]
  },
  "expected_shift_count_for_first_nullvector": 8,
  "integrand": "(4)/(n*(-1024*u**8 - 2048*u**7 - 1792*u**6 - 896*u**5 - 280*u**4 - 56*u**3 - 7*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 7,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-1024*u**8 - 2048*u**7 - 1792*u**6 - 896*u**5 - 280*u**4 - 56*u**3 - 7*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      16,
      16
    ],
    "G_inverse": [
      16,
      16
    ],
    "J": [
      8,
      8
    ],
    "U": [
      8,
      8
    ],
    "V": [
      8,
      8
    ],
    "X": [
      7,
      8
    ],
    "X_full": [
      8,
      8
    ],
    "embedding_E": [
      16,
      8
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 56,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "b1d47d296614a894cf49be6657320dd18664a19d1d50e3d959bfbbc17c5824b2",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "20373984027382963711975386092665040030573445756107263634531620579442688*n**7/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 348904476468933253567578486836888810523570258573336889741354002422956032*n**6/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 2254412797111364497235017981341550919531713010927990174092816122856341504*n**5/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 6646343632088337895713845244270663229628026778555965561451516534382919680*n**4/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 7829550723552810697521702558608377558160227419337682081259030682231898112*n**3/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 944967242569110450921863163802924025180649368560718244291548821370437632*n**2/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 7635448253752173154224957379935872940197832759627933676735684057868795904*n/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 3057540092219946207799351581614875146596272689008413497909478621959290880/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840)",
        "top_left": "1",
        "top_right": "58542850034708417135626909903215833573196275255402873131413131837440*n**7/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 1027023214118503386174336871519271600729438909815467311213988301398016*n**6/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 6920202471714314987936323653269267298028141030546122884274540873846784*n**5/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 22222523647077291821514243816231529522448090073957275214171912058746880*n**4/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 33398197305906959291920108476275175744333993999076831195689633613880320*n**3/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 16720169090256598288126652086481496849821165430411209116115600420545024*n**2/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 5624513594025445394802666051297778227065228318883814534400246211550464*n/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 3988208164030634371817080143655120190747777373620804668229337733580160/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840)"
      },
      "shape": [
        7,
        8
      ]
    },
    "X_full": {
      "entry_count": 64,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "0522c14b8009438bb1bc5d0e0d815973c084f8ae286ddc8811c5745054faa9e1",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "58542850034708417135626909903215833573196275255402873131413131837440*n**7/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 1027023214118503386174336871519271600729438909815467311213988301398016*n**6/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 6920202471714314987936323653269267298028141030546122884274540873846784*n**5/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 22222523647077291821514243816231529522448090073957275214171912058746880*n**4/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 33398197305906959291920108476275175744333993999076831195689633613880320*n**3/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) + 16720169090256598288126652086481496849821165430411209116115600420545024*n**2/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 5624513594025445394802666051297778227065228318883814534400246211550464*n/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840) - 3988208164030634371817080143655120190747777373620804668229337733580160/(474240004027617917932197159087816029848811824328622854671*n**7 + 13278720112773301702101520454458848835766731081201439930788*n**6 + 152705281296892969574167485226276761611317407433816559204062*n**5 + 929510407894131119147106431812119418503671175684100795155160*n**4 + 3210130587262945686483042569865426706046607238880448103267999*n**3 + 6227719732890678498285613093141200103974596877083475327539572*n**2 + 6197368372632910951537952474959579878064272920326443464840628*n + 2390169620299194306378273681802592790438011594616259187541840)"
      },
      "shape": [
        8,
        8
      ]
    }
  },
  "statistics": {
    "G_nonzero": 128,
    "G_shape": [
      16,
      16
    ],
    "X_rank": 7,
    "X_shape": [
      7,
      8
    ],
    "certificate_degree_n": 6,
    "certificate_degree_u": 49,
    "checks_passed": 7,
    "checks_total": 7,
    "denominator_degree": 8,
    "nullity": 1,
    "recurrence_degree": 7,
    "recurrence_order": 7
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-274877906944*n**7 - 4810363371520*n**6 - 33131377721344*n**5 - 113494510796800*n**4 - 199558206324736*n**3 - 162562331115520*n**2 - 37899139547136*n + 7695929180160",
    "-691489734656*n**7 - 13138304958464*n**6 - 101368073289728*n**5 - 409167441428480*n**4 - 927188636401664*n**3 - 1172677959090176*n**2 - 764013764739072*n - 198278258688000",
    "-745512370176*n**7 - 15283003588608*n**6 - 129392990748672*n**5 - 585110724280320*n**4 - 1522308412391424*n**3 - 2271837831094272*n**2 - 1792981912608768*n - 573197269155840",
    "-446530846720*n**7 - 9823678627840*n**6 - 89948057436160*n**5 - 443014416302080*n**4 - 1262356112684800*n**3 - 2068522968762880*n**2 - 1788084917525760*n - 619474554800640",
    "-160472023040*n**7 - 3771092541440*n**6 - 36943668554240*n**5 - 194720263082240*n**4 - 592783653109760*n**3 - 1033542630767360*n**2 - 943891424770560*n - 341745232066560",
    "-34601779968*n**7 - 865044499200*n**6 - 8993218874808*n**5 - 50123922200520*n**4 - 160587942137112*n**3 - 292866221732280*n**2 - 277655495519472*n - 103416069879360",
    "-4145004892*n**7 - 109842629638*n**6 - 1204123921126*n**5 - 7036145804170*n**4 - 23487670220518*n**3 - 44334972324832*n**2 - 43199240984424*n - 16414219372320",
    "124902511*n**7 + 3497270308*n**6 + 40218608542*n**5 + 244808921560*n**4 + 845465096959*n**3 + 1640219774452*n**2 + 1632226013748*n + 629508655440"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 7,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-1024*u**8 - 2048*u**7 - 1792*u**6 - 896*u**5 - 280*u**4 - 56*u**3 - 7*u**2 + u",
  "denominator_power": 6,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "full_certificate_location": "release/certificate_payload.json.gz#/objects/rational_certificate",
  "full_object_sha256": "db463474f363c27f41272c5fcd2138943968e12a5bd243ce9977ec96136ba2b9",
  "numerator_N": {
    "character_count": 13667,
    "leading_500_characters": "39614081257132168796771975168*n**6*u**49 + 485272495399869067760456695808*n**6*u**48 + 2911634972399214406562740174848*n**6*u**47 + 11403903641896923092370732351488*n**6*u**46 + 32786222970453653890565855510528*n**6*u**45 + 73769001683520721253773174898688*n**6*u**44 + 135243169753121322298584153980928*n**6*u**43 + 207694468889630129273769440575488*n**6*u**42 + 272595325105670200567993328467968*n**6*u**41 + 310439089393597383062771118112768*n**6*u**40 + 310388996796683013643773933518848*n**6*u**",
    "sha256": "49e57c8e5a4ac0d00b87aec5607c118ca186866d4bd9c6c9fd11a409f6cce362"
  },
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "7695929180160*x**7",
      "-551730806784000*x**8 - 198278258688000*x**7",
      "-2219107764142080*x**9 - 1594983705477120*x**8 - 286598634577920*x**7",
      "-2224480667566080*x**10 - 2398268219719680*x**9 - 861877641461760*x**8 - 103245759133440*x**7",
      "-853689174589440*x**11 - 1227178188472320*x**10 - 661525742223360*x**9 - 158490542407680*x**8 - 14239384669440*x**7",
      "-143769735266304*x**12 - 258336243056640*x**11 - 185679174696960*x**10 - 66728453406720*x**9 - 11990268971520*x**8 - 861800582328*x**7",
      "-10582799417344*x**13 - 22819161243648*x**12 - 20501590179840*x**11 - 9823678627840*x**10 - 2647788380160*x**9 - 380619579648*x**8 - 22797526906*x**7",
      "-274877906944*x**14 - 691489734656*x**13 - 745512370176*x**12 - 446530846720*x**11 - 160472023040*x**10 - 34601779968*x**9 - 4145004892*x**8 + 124902511*x**7"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 7
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-274877906944*theta**7 - 4810363371520*theta**6 - 33131377721344*theta**5 - 113494510796800*theta**4 - 199558206324736*theta**3 - 162562331115520*theta**2 - 37899139547136*theta + 7695929180160",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 7
      },
      {
        "polynomial_in_theta": "-691489734656*theta**7 - 8297876815872*theta**6 - 37059527966720*theta**5 - 75199508643840*theta**4 - 65635645128704*theta**3 - 14989255507968*theta**2 + 3595045109760*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 6
      },
      {
        "polynomial_in_theta": "-745512370176*theta**7 - 4845830406144*theta**6 - 8619986780160*theta**5 + 582431539200*theta**4 + 10651398782976*theta**3 + 3857971912704*theta**2 - 880472678400*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-446530846720*theta**7 - 446530846720*theta**6 + 2483827834880*theta**5 + 1981480632320*theta**4 - 2636777731840*theta**3 - 1243549162240*theta**2 + 308080120320*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-160472023040*theta**7 + 722124103680*theta**6 - 356047301120*theta**5 - 1451770333440*theta**4 + 922714132480*theta**3 + 458849690880*theta**2 - 135398269440*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-34601779968*theta**7 + 346017799680*theta**6 - 1207818382008*theta**5 + 1697649829680*theta**4 - 716905628712*theta**3 - 162195843600*theta**2 + 77854004928*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-4145004892*theta**7 + 64247575826*theta**6 - 383412952510*theta**5 + 1108788808610*theta**4 - 1602044390758*theta**3 + 1065266257244*theta**2 - 248700293520*theta",
        "shift": 6,
        "source": "P_6(theta-6)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "124902511*theta**7 - 2622952731*theta**6 + 21857939425*theta**5 - 91803345585*theta**4 + 202841677864*theta**3 - 220328029404*theta**2 + 89929807920*theta",
        "shift": 7,
        "source": "P_7(theta-7)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      16
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        16
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    4,
    28,
    616,
    15820,
    453208
  ],
  "status": "verified",
  "terms": [
    1,
    4,
    28,
    616,
    15820,
    453208,
    13894552,
    445970128,
    14796844588,
    503423385080,
    17467725995720,
    615756709476272,
    21990183407958584,
    793912445913712496,
    28928560840589374640,
    1062498482335560005024,
    39293868860176487815916,
    1462000514765724635982392,
    54687990558923499430218216,
    2055434531714445496708838640,
    77583216687515911219027951848,
    2939689135714969185929532445008,
    111775700909423797777044999484752,
    4263534996585393025571039315706720
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120605

### Defining data

```json
{
  "b": 64,
  "c": 24,
  "equation": "25*A(x)=24+64*x+A(x)^9",
  "linear_coefficient_d": "4",
  "q": 9,
  "r": 25,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 9,
    "Delta_3": 84,
    "Delta_4": 504,
    "Delta_5": 2016,
    "Delta_6": 5376,
    "Delta_7": 9216,
    "Delta_8": 9216,
    "Delta_9": 4096
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(4)*T(x)",
  "recursive_equation": "T=x+9*T^2+84*T^3+504*T^4+2016*T^5+5376*T^6+9216*T^7+9216*T^8+4096*T^9",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6",
      "Delta_7",
      "Delta_8",
      "Delta_9"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "Delta_7": 6,
      "Delta_8": 7,
      "Delta_9": 8,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 4,
      "pass": true,
      "published_term": 4
    },
    "2": {
      "enumerated": 36,
      "pass": true,
      "published_term": 36
    },
    "3": {
      "enumerated": 984,
      "pass": true,
      "published_term": 984
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "96113a0749dfb600632caa84d121e1f909a7bbe758d09c38a32961147580b1c7",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 4,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)",
        "root[3](l)"
      ]
    },
    "2": {
      "count": 36,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[3](Delta_2[4](l,l))",
        "root[3](Delta_2[5](l,l))",
        "root[3](Delta_2[6](l,l))",
        "root[3](Delta_2[7](l,l))",
        "root[3](Delta_2[8](l,l))"
      ]
    },
    "3": {
      "count": 984,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[3](Delta_3[79](l,l,l))",
        "root[3](Delta_3[80](l,l,l))",
        "root[3](Delta_3[81](l,l,l))",
        "root[3](Delta_3[82](l,l,l))",
        "root[3](Delta_3[83](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-9*u^1-84*u^2-504*u^3-2016*u^4-5376*u^5-9216*u^6-9216*u^7-4096*u^8",
  "coefficient_integral": "a(n)=(4)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(4)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-9*u^1-84*u^2-504*u^3-2016*u^4-5376*u^5-9216*u^6-9216*u^7-4096*u^8)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=24620140617029332500309060585087041536",
    "shape": [
      18,
      18
    ]
  },
  "expected_shift_count_for_first_nullvector": 9,
  "integrand": "(4)/(n*(-4096*u**9 - 9216*u**8 - 9216*u**7 - 5376*u**6 - 2016*u**5 - 504*u**4 - 84*u**3 - 9*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 8,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-4096*u**9 - 9216*u**8 - 9216*u**7 - 5376*u**6 - 2016*u**5 - 504*u**4 - 84*u**3 - 9*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      18,
      18
    ],
    "G_inverse": [
      18,
      18
    ],
    "J": [
      9,
      9
    ],
    "U": [
      9,
      9
    ],
    "V": [
      9,
      9
    ],
    "X": [
      8,
      9
    ],
    "X_full": [
      9,
      9
    ],
    "embedding_E": [
      18,
      9
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 72,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "2c504f47f34bf2a014631fc84c577736115a80b575b11749155e318cea2c6e5b",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "63731516014973343466497218104580311080485471023221867809610496788893672174549332184061542400000000000000*n**8/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 1504771905909092831847850983024812900511462510270516323282470063071100593010192565457008640000000000000000*n**7/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 14125270150834128527896817841053101713363774341593816806802596730516733238284652656859200102400000000000000*n**6/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 66417292130654695446366210460385880019215741184603859163691690065646779400586220257417703936000000000000000*n**5/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 158494375721757018615826996895826215977869431866031494292703740044697351565312178317164031129600000000000000*n**4/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 152884498284376839499089210665724497772550802421437940240423011673447754995421326232903975296000000000000000*n**3/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 48319324210173239978232500978932640607168058224205907739649823305707403906319644896569786150400000000000000*n**2/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 168488431697351282695775836895629508079852118730774033774580567756664916042248455417102359520000000000000000*n/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 62886279908207002565850013821470213412191374873949158130980824124366046297797182771660990720000000000000000/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120)",
        "top_left": "1",
        "top_right": "50765997873127619502003839570949462941567590192941854955988773817956699118494528661995962481630314496*n**8/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 1220566683961298001734909005705116118345308288640169300394151994921189959957902646169339636531572801536*n**7/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 11790177978808395624525092955698200306050401428356123336671849554357190711384826116680816380501627764736*n**6/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 58275539847426630092481730184539693777512465438161361076913385278882682654281768305797726653538647433216*n**5/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 154164768436107054541408768308405679203447290340138731604075279051872813858751768948306484703454450069504*n**4/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 202426172466541993140700498645714926261284308909267510220490379320785188459282162957344722528017326311424*n**3/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 88613712471645988832915441352478104592289770206919847455853868613591738095071740962255686259168001665024*n**2/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 35900907506892894740380773062362862394345700039136856424536569697352323895337863698478306755495133395456*n/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 22719093632838540615926262400285550619786552379902970724305178437427636736255955004867814160279819779840/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120)"
      },
      "shape": [
        8,
        9
      ]
    },
    "X_full": {
      "entry_count": 81,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "b89c2242ea686009df9bd334e5e057aed075dcad42d1a579a066f12b67f999ea",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "50765997873127619502003839570949462941567590192941854955988773817956699118494528661995962481630314496*n**8/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 1220566683961298001734909005705116118345308288640169300394151994921189959957902646169339636531572801536*n**7/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 11790177978808395624525092955698200306050401428356123336671849554357190711384826116680816380501627764736*n**6/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 58275539847426630092481730184539693777512465438161361076913385278882682654281768305797726653538647433216*n**5/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 154164768436107054541408768308405679203447290340138731604075279051872813858751768948306484703454450069504*n**4/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 202426172466541993140700498645714926261284308909267510220490379320785188459282162957344722528017326311424*n**3/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) + 88613712471645988832915441352478104592289770206919847455853868613591738095071740962255686259168001665024*n**2/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 35900907506892894740380773062362862394345700039136856424536569697352323895337863698478306755495133395456*n/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120) - 22719093632838540615926262400285550619786552379902970724305178437427636736255955004867814160279819779840/(1604010788611863159070053160140205004702320491975260148118646554770141896894475060099841*n**8 + 57744388390027073726521913765047380169283537711109365332271275971725108288201102163594276*n**7 + 875789890582077284852249025436551932567466988618492040872781018904497475704383382814513186*n**6 + 7275792937143411289541761134395969901329725751599780031866180772437363644313338872612878776*n**5 + 36008438193547716057963623391987462150562392724352615065115496508034915443384070624181330609*n**4 + 107924261900960600794869456826873553536390931982063403806015014791154227390647859943757701844*n**3 + 189472170393987723801990959488401575975456905794085629736367005635668241428762971999233618284*n**2 + 175773918259242412423532705500804225235299088792616908071433764057931229629284154985980976144*n + 64673714996830322573704543416853065789597562236442489172143829088332121282785234423225589120)"
      },
      "shape": [
        9,
        9
      ]
    }
  },
  "statistics": {
    "G_nonzero": 162,
    "G_shape": [
      18,
      18
    ],
    "X_rank": 8,
    "X_shape": [
      8,
      9
    ],
    "certificate_degree_n": 7,
    "certificate_degree_u": 64,
    "checks_passed": 11,
    "checks_total": 11,
    "denominator_degree": 9,
    "nullity": 1,
    "recurrence_degree": 8,
    "recurrence_order": 8
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-406239826673664*n**8 - 9749755840167936*n**7 - 95631864382881792*n**6 - 492904323030712320*n**5 - 1424692173997080576*n**4 - 2263677536456146944*n**3 - 1751568737221214208*n**2 - 416449128604631040*n + 71227287561830400",
    "-1218719480020992*n**8 - 31077346740535296*n**7 - 330340685723467776*n**6 - 1901236242151636992*n**5 - 6439919220683440128*n**4 - 13058724950941630464*n**3 - 15383091085476102144*n**2 - 9584186081289043968*n - 2420654909759815680",
    "-1599569317527552*n**8 - 43188371573243904*n**7 - 492045295063891968*n**6 - 3081748020140998656*n**5 - 11574224666431193088*n**4 - 26614874026099408896*n**3 - 36469569495083139072*n**2 - 27105592249843236864*n - 8307963641761136640",
    "-1199676988145664*n**8 - 34190794162151424*n**7 - 413977425872338944*n**6 - 2774786224859357184*n**5 - 11227623338293641216*n**4 - 27970822381405188096*n**3 - 41657190152355864576*n**2 - 33616055494337089536*n - 11095864301253795840",
    "-562348588193280*n**8 - 16870457645798400*n**7 - 215629441983889920*n**6 - 1528963328121062400*n**5 - 6551544516428701440*n**4 - 17275933605538137600*n**3 - 27164983822812622080*n**2 - 23024226418306444800*n - 7913273679798036480",
    "-168704576457984*n**8 - 5314194158426496*n**7 - 71315173459377792*n**6 - 530458737004486080*n**5 - 2379995126142774336*n**4 - 6551834362513441344*n**3 - 10709727353896915008*n**2 - 9383020505916624000*n - 3309421441517452800",
    "-31632108085872*n**8 - 1043859566833776*n**7 - 14642737144861896*n**6 - 113529393259532712*n**5 - 529135460482893768*n**4 - 1507078400303947464*n**3 - 2536946617107518784*n**2 - 2276900228093123808*n - 817795434380077440",
    "-3389154437772*n**8 - 116925828103134*n**7 - 1708133836637088*n**6 - 13736242936289916*n**5 - 66119013926493948*n**4 - 193624087607133246*n**3 - 333580914692146872*n**2 - 304962894619600104*n - 111028699381410720",
    "79551964831*n**8 + 2863870733916*n**7 + 43435372797726*n**6 + 360847712473416*n**5 + 1785862058491119*n**4 + 5352574401689004*n**3 + 9396996293697044*n**2 + 8717622514040304*n + 3207535221985920"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 8,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-4096*u**9 - 9216*u**8 - 9216*u**7 - 5376*u**6 - 2016*u**5 - 504*u**4 - 84*u**3 - 9*u**2 + u",
  "denominator_power": 7,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "full_certificate_location": "release/certificate_payload.json.gz#/objects/rational_certificate",
  "full_object_sha256": "424bb7c23675d5fe406943ff39e62a929ea00d4ff3bb277fd286bd08be855c69",
  "numerator_N": {
    "character_count": 25481,
    "leading_500_characters": "-873091227416114037923609044826021953536*n**7*u**64 - 13969459638657824606777744717216351256576*n**7*u**63 - 110009494654430368778374739648078766145536*n**7*u**62 - 568382389047890238688269488181740291751936*n**7*u**61 - 2166957858245081534999027423692884862304256*n**7*u**60 - 6500873574735244604997082271078654586912768*n**7*u**59 - 15981314204557476320617827249735025859493888*n**7*u**58 - 33104150852297629521279785017308267851808768*n**7*u**57 - 58966766078198608490944138488122604433440768*n**7",
    "sha256": "a0055cd20fd0cd269257d3756b3e28493f041f09dda60c2c2ca7a520103cb81f"
  },
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "71227287561830400*x**8",
      "-6455079759359508480*x**9 - 2420654909759815680*x**8",
      "-29539426281817374720*x**10 - 22154569711363031040*x**9 - 4153981820880568320*x**8",
      "-35068410631123107840*x**11 - 39451961960013496320*x**10 - 14794485735005061120*x**9 - 1849310716875632640*x**8",
      "-16673235078422200320*x**12 - 25009852617633300480*x**11 - 14068042097418731520*x**10 - 3517010524354682880*x**9 - 329719736658251520*x**8",
      "-3718899924404797440*x**13 - 6972937358258995200*x**12 - 5229703018694246400*x**11 - 1961138632010342400*x**10 - 367713493501939200*x**9 - 27578512012645440*x**8",
      "-408436530921603072*x**14 - 918982194573606912*x**13 - 861545807412756480*x**12 - 430772903706378240*x**11 - 121154879167418880*x**10 - 18173231875112832*x**9 - 1135826992194552*x**8",
      "-21124470987030528*x**15 - 55451736340955136*x**14 - 62383203383574528*x**13 - 38989502114734080*x**12 - 14621063293025280*x**11 - 3289739240930688*x**10 - 411217405116336*x**9 - 22029503845518*x**8",
      "-406239826673664*x**16 - 1218719480020992*x**15 - 1599569317527552*x**14 - 1199676988145664*x**13 - 562348588193280*x**12 - 168704576457984*x**11 - 31632108085872*x**10 - 3389154437772*x**9 + 79551964831*x**8"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 8
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-406239826673664*theta**8 - 9749755840167936*theta**7 - 95631864382881792*theta**6 - 492904323030712320*theta**5 - 1424692173997080576*theta**4 - 2263677536456146944*theta**3 - 1751568737221214208*theta**2 - 416449128604631040*theta + 71227287561830400",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 8
      },
      {
        "polynomial_in_theta": "-1218719480020992*theta**8 - 21327590900367360*theta**7 - 146923403980308480*theta**6 - 503568118480896000*theta**5 - 886451523460005888*theta**4 - 724055620292444160*theta**3 - 170679284976844800*theta**2 + 33569351811072000*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 7
      },
      {
        "polynomial_in_theta": "-1599569317527552*theta**8 - 17595262492803072*theta**7 - 66559856601563136*theta**6 - 88420637274439680*theta**5 + 21764236022710272*theta**4 + 117189845925691392*theta**3 + 43410943321030656*theta**2 - 8189699583098880*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 6
      },
      {
        "polynomial_in_theta": "-1199676988145664*theta**8 - 5398546446655488*theta**7 + 1710650520133632*theta**6 + 28658950272368640*theta**5 + 15349502278139904*theta**4 - 27989583173701632*theta**3 - 13924783001751552*theta**2 + 2793486539612160*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-562348588193280*theta**8 + 1124697176386560*theta**7 + 4811204587875840*theta**6 - 6873149411251200*theta**5 - 10805603976195840*theta**4 + 8348832331983360*theta**3 + 5104978370231040*theta**2 - 1148610490836480*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-168704576457984*theta**8 + 1433988899892864*theta**7 - 3411581435039232*theta**6 - 23431191174720*theta**5 + 7057474781825664*theta**4 - 3378777767394624*theta**3 - 2071317299845248*theta**2 + 562348588193280*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-31632108085872*theta**8 + 474481621288080*theta**7 - 2685800288402280*theta**6 + 7073290835868600*theta**5 - 8418241209297528*theta**4 + 3136850718515640*theta**3 + 802518297734160*theta**2 - 351467867620800*theta",
        "shift": 6,
        "source": "P_6(theta-6)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-3389154437772*theta**8 + 72866820412098*theta**7 - 628688148206706*theta**6 + 2787579525067470*theta**5 - 6749501062822938*theta**4 + 8730461831700672*theta**3 - 5429425409310744*theta**2 + 1220095597597920*theta",
        "shift": 7,
        "source": "P_7(theta-7)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "79551964831*theta**8 - 2227455015268*theta**7 + 25615732675582*theta**6 - 155921851068760*theta**5 + 538487249941039*theta**4 - 1044676402160692*theta**3 + 1039585076411508*theta**2 - 400941902748240*theta",
        "shift": 8,
        "source": "P_8(theta-8)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      15
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        15
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    4,
    36,
    984,
    31716,
    1140552
  ],
  "status": "verified",
  "terms": [
    1,
    4,
    36,
    984,
    31716,
    1140552,
    43895208,
    1768717872,
    73674176868,
    3146885203432,
    137085166193976,
    6066992348458704,
    272023207778276136,
    12330039492509279184,
    564072488005316830416,
    26010805156782400648800,
    1207726446293984191385700,
    56417048428864276998901800,
    2649564292708646727876610200,
    125027719851527116710700294800,
    5925036569802713483923377199800,
    281867894244228689457589414393200,
    13455903483569375477941107906442800,
    644401906020927239451103676874391200
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120606

### Defining data

```json
{
  "b": 81,
  "c": 35,
  "equation": "36*A(x)=35+81*x+A(x)^9",
  "linear_coefficient_d": "3",
  "q": 9,
  "r": 36,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 4,
    "Delta_3": 28,
    "Delta_4": 126,
    "Delta_5": 378,
    "Delta_6": 756,
    "Delta_7": 972,
    "Delta_8": 729,
    "Delta_9": 243
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(3)*T(x)",
  "recursive_equation": "T=x+4*T^2+28*T^3+126*T^4+378*T^5+756*T^6+972*T^7+729*T^8+243*T^9",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6",
      "Delta_7",
      "Delta_8",
      "Delta_9"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "Delta_7": 6,
      "Delta_8": 7,
      "Delta_9": 8,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 12,
      "pass": true,
      "published_term": 12
    },
    "3": {
      "enumerated": 180,
      "pass": true,
      "published_term": 180
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "d888b2db9bb5c75f19453ebb23b1fe8caa7599ca7ff92efd57622e0172590288",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 3,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ]
    },
    "2": {
      "count": 12,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[1](Delta_2[0](l,l))"
      ],
      "last_five": [
        "root[1](Delta_2[3](l,l))",
        "root[2](Delta_2[0](l,l))",
        "root[2](Delta_2[1](l,l))",
        "root[2](Delta_2[2](l,l))",
        "root[2](Delta_2[3](l,l))"
      ]
    },
    "3": {
      "count": 180,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[0](l,Delta_2[1](l,l)))"
      ],
      "last_five": [
        "root[2](Delta_3[23](l,l,l))",
        "root[2](Delta_3[24](l,l,l))",
        "root[2](Delta_3[25](l,l,l))",
        "root[2](Delta_3[26](l,l,l))",
        "root[2](Delta_3[27](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-4*u^1-28*u^2-126*u^3-378*u^4-756*u^5-972*u^6-729*u^7-243*u^8",
  "coefficient_integral": "a(n)=(3)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(3)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-4*u^1-28*u^2-126*u^3-378*u^4-756*u^5-972*u^6-729*u^7-243*u^8)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=1325632804992787927830650613",
    "shape": [
      18,
      18
    ]
  },
  "expected_shift_count_for_first_nullvector": 9,
  "integrand": "(3)/(n*(-243*u**9 - 729*u**8 - 972*u**7 - 756*u**6 - 378*u**5 - 126*u**4 - 28*u**3 - 4*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 8,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-243*u**9 - 729*u**8 - 972*u**7 - 756*u**6 - 378*u**5 - 126*u**4 - 28*u**3 - 4*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      18,
      18
    ],
    "G_inverse": [
      18,
      18
    ],
    "J": [
      9,
      9
    ],
    "U": [
      9,
      9
    ],
    "V": [
      9,
      9
    ],
    "X": [
      8,
      9
    ],
    "X_full": [
      9,
      9
    ],
    "embedding_E": [
      18,
      9
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 72,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "cac57860fc1373fb20c5e65a76c89cf1509386b8730e3baa3ad2d0dc0d1feadb",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "4826194423349782346076865865013144377241175988781766076270878486163959718274347438551544711086080*n**8/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 113951812773536527615703777368365908907083321957347254578617964256649048903699870076911472345088000*n**7/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 1070165696367445598155830300475003447997528475665383520245198542723776435545919721038453088725237760*n**6/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 5037916004889285173632040802453155941787581092447204021083432371010509002836644543895028213680701440*n**5/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 12053602755203603838153115874446695522930598231222219725628542702525030830992242401587905761189560320*n**4/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 11715280997212655555773143462923634882098913394463151425892780124704531911479433825082921024120422400*n**3/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 3536782699885516169868180412223540318880474601393335981938847629844662098921775223564312221224796160*n**2/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 12849638365771944136097897009868805747085499767706308828527131448101074820257079544879407981385482240*n/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 4912036272402288286874247048587350930271886698875027101708532223004170319388300925299388253103718400/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720)",
        "top_left": "1",
        "top_right": "34989667660512253988554206846744063157672929389694085330373543530170220476753703851898753220449*n**8/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 841449995225062853153286688765394885136182883890869264835170094577129000865655564607931811935316*n**7/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 8135162642816457248826794959593555236239830791755118952101380357679994378007609270342595459610682*n**6/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 40288794793429630685957998768201193754295813902802355848284302415144272166867956218615028016269840*n**5/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 107036385417411246500912475318442675556584751937274190451144233308715255454718425191047026227524441*n**4/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 142087670979293429807285706644466044142255011197359552303690104865705307828064806983541907636661164*n**3/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 65487900889760991136316734340155115253018304239579361461828228788873554918388824207697190983417868*n**2/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 21150740032920156253834573749782657024959433080032022512636822921430296101343990488653323533368080*n/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 14646220849321781576694462227195007226863217354750556269151347760458340615086883513205444970953600/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720)"
      },
      "shape": [
        8,
        9
      ]
    },
    "X_full": {
      "entry_count": 81,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "8129648251bfe3e9c909fe1937882c1dd4d8793b73e7aff6549161312f1b1348",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "34989667660512253988554206846744063157672929389694085330373543530170220476753703851898753220449*n**8/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 841449995225062853153286688765394885136182883890869264835170094577129000865655564607931811935316*n**7/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 8135162642816457248826794959593555236239830791755118952101380357679994378007609270342595459610682*n**6/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 40288794793429630685957998768201193754295813902802355848284302415144272166867956218615028016269840*n**5/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 107036385417411246500912475318442675556584751937274190451144233308715255454718425191047026227524441*n**4/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 142087670979293429807285706644466044142255011197359552303690104865705307828064806983541907636661164*n**3/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) + 65487900889760991136316734340155115253018304239579361461828228788873554918388824207697190983417868*n**2/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 21150740032920156253834573749782657024959433080032022512636822921430296101343990488653323533368080*n/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720) - 14646220849321781576694462227195007226863217354750556269151347760458340615086883513205444970953600/(242903974833511253169071628553551588882703331357238097664619391932816165144968238721*n**8 + 8744543094006405114086578627927857199777319928860571515926298109581381945218856593956*n**7 + 132625570259097144230313109190239167529956018921052001324882187995317626169152658341666*n**6 + 1101812429844807044374908907118910007171942311036432011006713561807254125097575930838456*n**5 + 5452951331037494122392488989398679618827807085638638054473040729499790091339391991047729*n**4 + 16343551042697971158227815455597165106383810947040408163266251166807602855614042974103764*n**3 + 28692789123233683269343417051259727885180448313242393048535501052671976691584228230679404*n**2 + 26618389178155497167279545343412397316122161863451579694479651445565726641246199472002064*n + 9793888265287173727776968063279200063750598320323840097837453882731147778645119385230720)"
      },
      "shape": [
        9,
        9
      ]
    }
  },
  "statistics": {
    "G_nonzero": 162,
    "G_shape": [
      18,
      18
    ],
    "X_rank": 8,
    "X_shape": [
      8,
      9
    ],
    "certificate_degree_n": 7,
    "certificate_degree_u": 64,
    "checks_passed": 11,
    "checks_total": 11,
    "denominator_degree": 9,
    "nullity": 1,
    "recurrence_degree": 8,
    "recurrence_order": 8
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-22876792454961*n**8 - 549043018919064*n**7 - 5385366401619708*n**6 - 27757174845352680*n**5 - 80229423696855174*n**4 - 127475638246726056*n**3 - 98636991848159292*n**2 - 23451714129423960*n + 4011058905828975",
    "-79080270214680*n**8 - 2016546890474340*n**7 - 21435146576523540*n**6 - 123367418209073430*n**5 - 417873481536198870*n**4 - 847354550993031060*n**3 - 998178021865648260*n**2 - 621898671122461845*n - 157071456966455325",
    "-119596704954300*n**8 - 3229111033766100*n**7 - 36789275296219950*n**6 - 230416340617231650*n**5 - 865382398460584200*n**4 - 1989942668577378900*n**3 - 2726759193815725425*n**2 - 2026632721317014475*n - 621170377267907250",
    "-103355177121000*n**8 - 2945622547948500*n**7 - 35665192045791000*n**6 - 239054782726588500*n**5 - 967287870188199000*n**4 - 2409756401111487750*n**3 - 3588871262101051500*n**2 - 2896107372282710250*n - 955936499156572500",
    "-55824555543750*n**8 - 1674736666312500*n**7 - 21405615686831250*n**6 - 151780763795062500*n**5 - 650374284622584375*n**4 - 1714988417115093750*n**3 - 2696678146083403125*n**2 - 2285623603448718750*n - 785553650076825000",
    "-19297377225000*n**8 - 607867382587500*n**7 - 8157430183612500*n**6 - 60676850416218750*n**5 - 272237213163431250*n**4 - 749435622101381250*n**3 - 1225038781188731250*n**2 - 1073282598576562500*n - 378550216563750000",
    "-4169186437500*n**8 - 137583152437500*n**7 - 1929947284781250*n**6 - 14963441745656250*n**5 - 69741301447781250*n**4 - 198636487006781250*n**3 - 334375546517250000*n**2 - 300100819228875000*n - 107787366697500000",
    "-514714375000*n**8 - 17757645937500*n**7 - 259416045000000*n**6 - 2086137361875000*n**5 - 10041562741875000*n**4 - 29405889600937500*n**3 - 50661277073750000*n**2 - 46315028891250000*n - 16862042925000000",
    "26495939759*n**8 + 953853831324*n**7 + 14466783108414*n**6 + 120185582746824*n**5 + 594807351649791*n**4 + 1782752810744556*n**3 + 3129806388092116*n**2 + 2903531062550256*n + 1068316291082880"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 8,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-243*u**9 - 729*u**8 - 972*u**7 - 756*u**6 - 378*u**5 - 126*u**4 - 28*u**3 - 4*u**2 + u",
  "denominator_power": 7,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "full_certificate_location": "release/certificate_payload.json.gz#/objects/rational_certificate",
  "full_object_sha256": "de5b395859d8a8c4f01e479fb1257ff27b5f66ec0e6065f1c5c44ad9d9fb4955",
  "numerator_N": {
    "character_count": 22577,
    "leading_500_characters": "-127173474825648610542883299603*n**7*u**64 - 2713034129613837024914843724864*n**7*u**63 - 28486858360945288761605859111072*n**7*u**62 - 196242802042067544802173696098496*n**7*u**61 - 997567577047176686077716288500688*n**7*u**60 - 3990270308188706744310865154002752*n**7*u**59 - 13079219343507427661907835782564576*n**7*u**58 - 36123558186830038304316879780416448*n**7*u**57 - 85793445188879571351626938788219732*n**7*u**56 - 177941869052153452052845076403690528*n**7*u**55 - 3262260063772746428494602",
    "sha256": "59e743b552ce8105e978c475badc5f169b69dcde459be39d34d4fff48f89f50f"
  },
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "4011058905828975*x**8",
      "-363508228979510895*x**9 - 157071456966455325*x**8",
      "-1663468916430505905*x**10 - 1437565730248585350*x**9 - 310585188633953625*x**8",
      "-1974825457913578410*x**11 - 2559958926925009050*x**10 - 1106155091881176750*x**9 - 159322749859428750*x**8",
      "-938928468843224055*x**12 - 1622839328864831700*x**11 - 1051840305745724250*x**10 - 302999265029632500*x**9 - 32731402086534375*x**8",
      "-209424325596026310*x**13 - 452459962707464250*x**12 - 391014782586697500*x**11 - 168957004821412500*x**10 - 36503056597218750*x**9 - 3154585138031250*x**8",
      "-23000496591939678*x**14 - 59630917090213980*x**13 - 64416114140663250*x**12 - 37112164525485000*x**11 - 12027090355481250*x**10 - 2078756357737500*x**9 - 149704675968750*x**8",
      "-1189593207657972*x**15 - 3598152294767940*x**14 - 4664271493217700*x**13 - 3359043256432500*x**12 - 1451438444137500*x**11 - 376298855887500*x**10 - 54199423687500*x**9 - 3345643437500*x**8",
      "-22876792454961*x**16 - 79080270214680*x**15 - 119596704954300*x**14 - 103355177121000*x**13 - 55824555543750*x**12 - 19297377225000*x**11 - 4169186437500*x**10 - 514714375000*x**9 + 26495939759*x**8"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 8
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-22876792454961*theta**8 - 549043018919064*theta**7 - 5385366401619708*theta**6 - 27757174845352680*theta**5 - 80229423696855174*theta**4 - 127475638246726056*theta**3 - 98636991848159292*theta**2 - 23451714129423960*theta + 4011058905828975",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 8
      },
      {
        "polynomial_in_theta": "-79080270214680*theta**8 - 1383904728756900*theta**7 - 9533565909214200*theta**6 - 32675528317871250*theta**5 - 57520066887110520*theta**4 - 46982521443078900*theta**3 - 11075037526917000*theta**2 + 2178248116708125*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 7
      },
      {
        "polynomial_in_theta": "-119596704954300*theta**8 - 1315563754497300*theta**7 - 4976551778376150*theta**6 - 6611040079418250*theta**5 + 1627269844227300*theta**4 + 8762058182310300*theta**3 + 3245752292984775*theta**2 - 612328002276375*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 6
      },
      {
        "polynomial_in_theta": "-103355177121000*theta**8 - 465098297044500*theta**7 + 147376826635500*theta**6 + 2469040342335000*theta**5 + 1322398064106000*theta**4 - 2411372690354250*theta**3 - 1199654930234250*theta**2 + 240665861677500*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-55824555543750*theta**8 + 111649111087500*theta**7 + 477610086318750*theta**6 - 682300123312500*theta**5 - 1072676364834375*theta**4 + 828791721056250*theta**3 + 506773120021875*theta**2 - 114022994793750*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-19297377225000*theta**8 + 164027706412500*theta**7 - 390235850550000*theta**6 - 2680191281250*theta**5 + 807273613912500*theta**4 - 386483582756250*theta**3 - 236928909262500*theta**2 + 64324590750000*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-4169186437500*theta**8 + 62537796562500*theta**7 - 353994811406250*theta**6 + 932276411718750*theta**5 - 1109544042468750*theta**4 + 413444321718750*theta**3 + 105773804062500*theta**2 - 46324293750000*theta",
        "shift": 6,
        "source": "P_6(theta-6)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-514714375000*theta**8 + 11066359062500*theta**7 - 95479516562500*theta**6 + 423352573437500*theta**5 - 1025053677812500*theta**4 + 1325904230000000*theta**3 - 824572428750000*theta**2 + 185297175000000*theta",
        "shift": 7,
        "source": "P_7(theta-7)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "26495939759*theta**8 - 741886313252*theta**7 + 8531692602398*theta**6 - 51932041927640*theta**5 + 179351016228671*theta**4 - 347944680915188*theta**3 + 346248940770612*theta**2 - 133539536385360*theta",
        "shift": 8,
        "source": "P_8(theta-8)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      15
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        15
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    12,
    180,
    3018,
    56238
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    12,
    180,
    3018,
    56238,
    1121484,
    23406804,
    504914175,
    11167352013,
    251879507880,
    5771456609880,
    133970974830420,
    3143760834627420,
    74454455230816008,
    1777349666975945784,
    42721359085344132657,
    1033093137613339252467,
    25116105553098288701700,
    613521274585967463941820,
    15050714233750522894763910,
    370639874968259588777874690,
    9159207116966261494311363300,
    227058949790969644676971410300
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A120607

### Defining data

```json
{
  "b": 81,
  "c": 36,
  "equation": "37*A(x)=36+81*x+A(x)^10",
  "linear_coefficient_d": "3",
  "q": 10,
  "r": 37,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "shift equation, integral finite-color grammar, coefficient comparison",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_10": 729,
    "Delta_2": 5,
    "Delta_3": 40,
    "Delta_4": 210,
    "Delta_5": 756,
    "Delta_6": 1890,
    "Delta_7": 3240,
    "Delta_8": 3645,
    "Delta_9": 2430
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(3)*T(x)",
  "recursive_equation": "T=x+5*T^2+40*T^3+210*T^4+756*T^5+1890*T^6+3240*T^7+3645*T^8+2430*T^9+729*T^10",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2",
      "Delta_3",
      "Delta_4",
      "Delta_5",
      "Delta_6",
      "Delta_7",
      "Delta_8",
      "Delta_9",
      "Delta_10"
    ],
    "colors": "branch multiplicity labels distinguish constructors of the same arity",
    "false_leaves": "restored as the q-k unused positions of a full Delta_q slot mask",
    "true_leaf": "l",
    "validity": "depth-first tree word; total weight -1; every proper prefix has nonnegative open-slot balance",
    "weights": {
      "Delta_10": 9,
      "Delta_2": 1,
      "Delta_3": 2,
      "Delta_4": 3,
      "Delta_5": 4,
      "Delta_6": 5,
      "Delta_7": 6,
      "Delta_8": 7,
      "Delta_9": 8,
      "l": -1
    }
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 3,
      "pass": true,
      "published_term": 3
    },
    "2": {
      "enumerated": 15,
      "pass": true,
      "published_term": 15
    },
    "3": {
      "enumerated": 270,
      "pass": true,
      "published_term": 270
    }
  },
  "encoding": "prefix depth-first Delta word; l=true leaf; constructor suffix [c] is a finite color; false slots are suppressed and recoverable from the model metadata",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "c2d033d6e6201daedfaacc568eca41c5fcae02a1c95ebe2d905f2aa38af802ea",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 3,
      "first_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)",
        "root[2](l)"
      ]
    },
    "2": {
      "count": 15,
      "first_five": [
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))"
      ],
      "last_five": [
        "root[2](Delta_2[0](l,l))",
        "root[2](Delta_2[1](l,l))",
        "root[2](Delta_2[2](l,l))",
        "root[2](Delta_2[3](l,l))",
        "root[2](Delta_2[4](l,l))"
      ]
    },
    "3": {
      "count": 270,
      "first_five": [
        "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[3](l,Delta_2[0](l,l)))",
        "root[0](Delta_2[4](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[2](Delta_3[35](l,l,l))",
        "root[2](Delta_3[36](l,l,l))",
        "root[2](Delta_3[37](l,l,l))",
        "root[2](Delta_3[38](l,l,l))",
        "root[2](Delta_3[39](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "D": "1-5*u^1-40*u^2-210*u^3-756*u^4-1890*u^5-3240*u^6-3645*u^7-2430*u^8-729*u^9",
  "coefficient_integral": "a(n)=(3)/(2*pi*i*n) * integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0",
  "ogf_integral": "A(x)=1-(3)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-5*u^1-40*u^2-210*u^3-756*u^4-1890*u^5-3240*u^6-3645*u^7-2430*u^8-729*u^9)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "G": {
    "definition": "coeff(rho*a-rho'*b), with deg(a),deg(b)<deg(rho)",
    "invertibility_witness": "resultant(rho,rho')=239315126314637039482020029531121441",
    "shape": [
      20,
      20
    ]
  },
  "expected_shift_count_for_first_nullvector": 10,
  "integrand": "(3)/(n*(-729*u**10 - 2430*u**9 - 3645*u**8 - 3240*u**7 - 1890*u**6 - 756*u**5 - 210*u**4 - 40*u**3 - 5*u**2 + u)^n)",
  "kernel_class": "polynomial_power",
  "q3_algorithm_relation": "same exact G/U/V construction; replace hard-coded normalized rho_q by this rho",
  "remainder_dimension": 9,
  "required_change": "parameterize the existing polynomial-kernel entry point; no change to Lower(w,m)=U*w-J*V*w/m",
  "status": "verified",
  "term_shift_ratio": "n/((n+s)*(-729*u**10 - 2430*u**9 - 3645*u**8 - 3240*u**7 - 1890*u**6 - 756*u**5 - 210*u**4 - 40*u**3 - 5*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `release/certificate_payload.json.gz#/objects/matrices`

```json
{
  "canonical_source": "release/certificate_payload.json.gz#/objects/matrices",
  "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
  "matrix_shapes": {
    "G": [
      20,
      20
    ],
    "G_inverse": [
      20,
      20
    ],
    "J": [
      10,
      10
    ],
    "U": [
      10,
      10
    ],
    "V": [
      10,
      10
    ],
    "X": [
      9,
      10
    ],
    "X_full": [
      10,
      10
    ],
    "embedding_E": [
      20,
      10
    ]
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 90,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "e827a11822d72c7b85cbc72d25cab64ee8c25a04df1b0aa078c67173fb297807",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "65903350699833720072322873434877772844091567696164952963869741770904953324492593141893489578970623035858076574686172731550756000000000000*n**9/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 2049594206764828694249241363824698735451247755350730037176348969075144048391719646712887525905986376415186181472739971951228511600000000000*n**8/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 26261937396646064512224945477711246980018291350955225482601397382143403535632111078063381414968887763356338741572304110146719390800000000000*n**7/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 178099717199701362043700844992681414209691411117859945710877232319013563590857290627610478130817457505796393226576955799479485871160000000000*n**6/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 678316024767741102117616791965116007068573661130264472839625736557226115333729625994962655367312387890253342357094381072030484341866000000000*n**5/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 1384477431537580391077267717379795091249248265803509335492837250184567712834664018314513131601837742474292582022826009301132507771232600000000*n**4/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 1125713047894951999354494043301930810609521445345124785454848668182169540083337642428756375117250303754108295800754908623739970242781360000000*n**3/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 574012925105793011839854629259706519967758920959926656117677873670628190184732445296637714022598796757420604458438785095929801622970104000000*n**2/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 1406418430622024944174034327468949840023771313486802479409973723428114281570610167164339317923780343789385915309885247610426668362027343360000*n/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 506930537778124617763194048710963484546456513395953009211942354529850766268487232759354933211634318344131846668034501968929747848014795776000/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720)",
        "top_left": "1",
        "top_right": "173331061065065246777132488617576841960988004770142661684311618254631746140856586709685089383424360018632982048372610476048090000000000*n**9/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 5468391583514334490702891507871858123223360680433725736472191940955297527593449010754993956897558035278689058487336598328124435000000000*n**8/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 71567541721698840105422350471628661669948130586981286089117746290968406938517764969039052392504873255215150380066732468469606303000000000*n**7/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 501881747158758848395589511344915494318268094823374630468911749524374033220146218040132227933828320572022578093625145092159437913500000000*n**6/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 2027111202197788529259556940716975587620195800930663418219676816128577290446080985015387305531872717331352472613045335857937562824977000000*n**5/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 4678710941912652699230809882164746000764607238939834190860308303694607151038880654379747901990074097014245764394901730544584999525947500000*n**4/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 5593422515282696186245818211185365313226254263953554976429980052505313550933344328809310476425839319964906127393334654401825902204619200000*n**3/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 2306999488670316475894039692986641424751143783876737023009907648639325341915235615767397573471144828493841451052317851747459132024280100000*n**2/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 878252470101351183148359102140754850431697888555426707641492406830420855217658204148485106044217662837134047109705463343354729220948273600*n/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 550484148153108090814994332895335427772408945912874614379030991312846532746111699319428647355777272834248736671156149666373866729172153600/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720)"
      },
      "shape": [
        9,
        10
      ]
    },
    "X_full": {
      "entry_count": 100,
      "full_entries_location": "release/certificate_payload.json.gz#/objects/matrices",
      "full_object_sha256": "63c33009dd76f91a846d7999e4a78f5e3f8ef771332d983b58f973b62bb0b6f6",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "173331061065065246777132488617576841960988004770142661684311618254631746140856586709685089383424360018632982048372610476048090000000000*n**9/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 5468391583514334490702891507871858123223360680433725736472191940955297527593449010754993956897558035278689058487336598328124435000000000*n**8/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 71567541721698840105422350471628661669948130586981286089117746290968406938517764969039052392504873255215150380066732468469606303000000000*n**7/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 501881747158758848395589511344915494318268094823374630468911749524374033220146218040132227933828320572022578093625145092159437913500000000*n**6/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 2027111202197788529259556940716975587620195800930663418219676816128577290446080985015387305531872717331352472613045335857937562824977000000*n**5/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 4678710941912652699230809882164746000764607238939834190860308303694607151038880654379747901990074097014245764394901730544584999525947500000*n**4/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 5593422515282696186245818211185365313226254263953554976429980052505313550933344328809310476425839319964906127393334654401825902204619200000*n**3/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) + 2306999488670316475894039692986641424751143783876737023009907648639325341915235615767397573471144828493841451052317851747459132024280100000*n**2/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 878252470101351183148359102140754850431697888555426707641492406830420855217658204148485106044217662837134047109705463343354729220948273600*n/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720) - 550484148153108090814994332895335427772408945912874614379030991312846532746111699319428647355777272834248736671156149666373866729172153600/(7630129240941452956413105721716561998964685638846289840484616351348724479934690624213807139423154005824488668287546675369*n**9 + 343355815842365383038589757477245289953410853748083042821807735810692601597061078089621321274041930262101990072939600391605*n**8 + 6638212439619064072079401977893408939099276505796272161221616225673390297543180843066012211298143985067305141410165607571030*n**7 + 72104721326896730438103849070221510890216279287097438992579624520245446335382826398820477467548805355041417915317316082237050*n**6 + 482781167462088552911126438330172027360492554426721297076983130398887844018907679865880219132721223410532871508557940790622737*n**5 + 2054984557816556817485959698501313060371163959682277011288519298826995220558410552366383607825140952618680410586543508343755925*n**4 + 5521771929084510675497036348691841587410763703120283031761907161144044931639136910931047950657748090935065959466331778031037920*n**3 + 8947852560852041881985649079857012256185886848675044095936309595226649197619411695015531632401532702630377861300805986205226300*n**2 + 7832907555648713010182740419376901350649171124384268839285335515502168181713434962242913277960463746683280279135956515813606544*n + 2768821298952834448823187804296506018184305124624541657315057581577425139278700533714706334753874125633590447948184937557902720)"
      },
      "shape": [
        10,
        10
      ]
    }
  },
  "statistics": {
    "G_nonzero": 200,
    "G_shape": [
      20,
      20
    ],
    "X_rank": 9,
    "X_shape": [
      9,
      10
    ],
    "certificate_degree_n": 8,
    "certificate_degree_u": 81,
    "checks_passed": 11,
    "checks_total": 11,
    "denominator_degree": 10,
    "nullity": 1,
    "recurrence_degree": 9,
    "recurrence_order": 9
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/certificate_payload.json.gz#/objects/p_recurrence`

```json
{
  "coefficients": [
    "-47829690000000000*n**9 - 1506635235000000000*n**8 - 19930631823000000000*n**7 - 143783222593500000000*n**6 - 613933066696257000000*n**5 - 1571056697695747500000*n**4 - 2309791335910747200000*n**3 - 1713370388457968100000*n**2 - 411585265795186382400*n + 60765412591845561600",
    "-191318760000000000*n**9 - 6313519080000000000*n**8 - 88663490676000000000*n**7 - 692159387220000000000*n**6 - 3292052227343460000000*n**5 - 9831404481830820000000*n**4 - 18310856628451269600000*n**3 - 20372865928799666400000*n**2 - 12226537462320826214400*n - 3015557810621069414400",
    "-340122240000000000*n**9 - 11734217280000000000*n**8 - 173827973808000000000*n**7 - 1447530492744000000000*n**6 - 7447206055655520000000*n**5 - 24476155577632080000000*n**4 - 51226851223679097600000*n**3 - 65597034406576752000000*n**2 - 46418781904152652800000*n - 13734552585302438400000",
    "-352719360000000000*n**9 - 12697896960000000000*n**8 - 197390571840000000000*n**7 - 1735467431040000000000*n**6 - 9487162552533120000000*n**5 - 33339535474129920000000*n**4 - 75015844564847155200000*n**3 - 103634639243015731200000*n**2 - 79107568422219187200000*n - 25085978785653811200000",
    "-235146240000000000*n**9 - 8817984000000000000*n**8 - 143223655680000000000*n**7 - 1319336968320000000000*n**6 - 7573537052847360000000*n**5 - 27986631106654080000000*n**4 - 66226976396582400000000*n**3 - 96067552211164800000000*n**2 - 76690890743120640000000*n - 25252524724331520000000",
    "-104509440000000000*n**9 - 4075868160000000000*n**8 - 68918750208000000000*n**7 - 661246903296000000000*n**6 - 3952929861522432000000*n**5 - 15196973535636480000000*n**4 - 37340117559198720000000*n**3 - 56065821201331200000000*n**2 - 46122233705146368000000*n - 15556186877091840000000",
    "-30965760000000000*n**9 - 1254113280000000000*n**8 - 22008139776000000000*n**7 - 218910504960000000000*n**6 - 1354483759104000000000*n**5 - 5377809991680000000000*n**4 - 13607859492864000000000*n**3 - 20968464384000000000000*n**2 - 17628833488896000000000*n - 6046776852480000000000",
    "-5898240000000000*n**9 - 247726080000000000*n**8 - 4499816448000000000*n**7 - 46227062784000000000*n**6 - 294661226496000000000*n**5 - 1201815552000000000000*n**4 - 3114132160512000000000*n**3 - 4897050525696000000000*n**2 - 4185946128384000000000*n - 1453904363520000000000",
    "-655360000000000*n**9 - 28508160000000000*n**8 - 534773760000000000*n**7 - 5656412160000000000*n**6 - 37007523840000000000*n**5 - 154436567040000000000*n**4 - 408128061440000000000*n**3 - 652420055040000000000*n**2 - 565051392000000000000*n - 198180864000000000000",
    "27001782375529*n**9 + 1215080206898805*n**8 + 23491550666710230*n**7 + 255166843448749050*n**6 + 1708483776246846417*n**5 + 7272255038289347925*n**4 + 19540649869522826720*n**3 + 31664990191782858300*n**2 + 27719381743941058704*n + 9798406788431963520"
  ],
  "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
  "order": 9,
  "valid_from_n": 1
}
```

### Rational telescoping certificate

Canonical source: `release/certificate_payload.json.gz#/objects/rational_certificate`

```json
{
  "denominator_base": "-729*u**10 - 2430*u**9 - 3645*u**8 - 3240*u**7 - 1890*u**6 - 756*u**5 - 210*u**4 - 40*u**3 - 5*u**2 + u",
  "denominator_power": 8,
  "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
  "full_certificate_location": "release/certificate_payload.json.gz#/objects/rational_certificate",
  "full_object_sha256": "c31f4d56b4d59da720384a6aa38f24085dddea5fdf597d35dfa458514816cf3d",
  "numerator_N": {
    "character_count": 39378,
    "leading_500_characters": "381520424476945831628649898809000000000*n**8*u**81 + 10301051460877537453973547267843000000000*n**8*u**80 + 137347352811700499386313963571240000000000*n**8*u**79 + 1205604541347148827946533680236440000000000*n**8*u**78 + 7836429518756467381652468921536860000000000*n**8*u**77 + 40227004862949865892482673797222548000000000*n**8*u**76 + 169847353865788322657149067143828536000000000*n**8*u**75 + 606597692377815438061246668370816200000000000*n**8*u**74 + 1870342884831597600688843894143349950000000000",
    "sha256": "f13007933950a495ba2c9b7cda90dd19c7a890503bb70059b348e8344e7ec41a"
  },
  "status": "verified"
}
```

### Scalar linear ODE

Canonical source: `release/certificate_payload.json.gz#/objects/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "60765412591845561600*x**9",
      "-6785005073897406182400*x**10 - 3015557810621069414400*x**9",
      "-34765586231546797200000*x**11 - 30902743316930486400000*x**10 - 6867276292651219200000*x**9",
      "-47624162850889657200000*x**12 - 63498883801186209600000*x**11 - 28221726133860537600000*x**10 - 4180996464275635200000*x**9",
      "-26966441197320817500000*x**13 - 47940339906348120000000*x**12 - 31960226604232080000000*x**11 - 9469696771624320000000*x**10 - 1052188530180480000000*x**9",
      "-7475401032758757000000*x**14 - 16612002295019460000000*x**13 - 14766224262239520000000*x**12 - 6562766338773120000000*x**11 - 1458392519727360000000*x**10 - 129634890642432000000*x**9",
      "-1089648823126500000000*x**15 - 2905730195004000000000*x**14 - 3228589105560000000000*x**13 - 1913237988480000000000*x**12 - 637745996160000000000*x**11 - 113377065984000000000*x**10 - 8398301184000000000*x**9",
      "-84213735183000000000*x**16 - 261998287236000000000*x**15 - 349331049648000000000*x**14 - 258763740480000000000*x**13 - 115006106880000000000*x**12 - 30668295168000000000*x**11 - 4543451136000000000*x**10 - 288473088000000000*x**9",
      "-3228504075000000000*x**17 - 11479125600000000000*x**16 - 17856417600000000000*x**15 - 15872371200000000000*x**14 - 8817984000000000000*x**13 - 3135283200000000000*x**12 - 696729600000000000*x**11 - 88473600000000000*x**10 - 4915200000000000*x**9",
      "-47829690000000000*x**18 - 191318760000000000*x**17 - 340122240000000000*x**16 - 352719360000000000*x**15 - 235146240000000000*x**14 - 104509440000000000*x**13 - 30965760000000000*x**12 - 5898240000000000*x**11 - 655360000000000*x**10 + 27001782375529*x**9"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 9
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "-47829690000000000*theta**9 - 1506635235000000000*theta**8 - 19930631823000000000*theta**7 - 143783222593500000000*theta**6 - 613933066696257000000*theta**5 - 1571056697695747500000*theta**4 - 2309791335910747200000*theta**3 - 1713370388457968100000*theta**2 - 411585265795186382400*theta + 60765412591845561600",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 9
      },
      {
        "polynomial_in_theta": "-191318760000000000*theta**9 - 4591650240000000000*theta**8 - 45042813396000000000*theta**7 - 232222710888000000000*theta**6 - 671578303499460000000*theta**5 - 1068152151593520000000*theta**4 - 828309111182589600000*theta**3 - 198549223980177600000*theta**2 + 33079472918677785600*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 8
      },
      {
        "polynomial_in_theta": "-340122240000000000*theta**9 - 5612016960000000000*theta**8 - 35058099888000000000*theta**7 - 99609049512000000000*theta**6 - 107147036999520000000*theta**5 + 44957598603120000000*theta**4 + 154584881236742400000*theta**3 + 57469581345513600000*theta**2 - 9245735585856000000*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 7
      },
      {
        "polynomial_in_theta": "-352719360000000000*theta**9 - 3174474240000000000*theta**8 - 6922117440000000000*theta**7 + 9832052160000000000*theta**6 + 43799543786880000000*theta**5 + 16375613546880000000*theta**4 - 42047905348915200000*theta**3 - 21077288544614400000*theta**2 + 3567295439769600000*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 6
      },
      {
        "polynomial_in_theta": "-235146240000000000*theta**9 - 352719360000000000*theta**8 + 3507598080000000000*theta**7 + 4614744960000000000*theta**6 - 13820583087360000000*theta**5 - 14538533546880000000*theta**4 + 13675987745280000000*theta**3 + 8772395022720000000*theta**2 - 1623743573760000000*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 5
      },
      {
        "polynomial_in_theta": "-104509440000000000*theta**9 + 627056640000000000*theta**8 + 57480192000000000*theta**7 - 4849238016000000000*theta**6 + 3092098157568000000*theta**5 + 9576426424320000000*theta**4 - 5226787077120000000*theta**3 - 4017255782400000000*theta**2 + 844728901632000000*theta",
        "shift": 5,
        "source": "P_5(theta-5)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-30965760000000000*theta**9 + 418037760000000000*theta**8 - 1942327296000000000*theta**7 + 3127928832000000000*theta**6 + 1310238720000000000*theta**5 - 7081482240000000000*theta**4 + 2706794496000000000*theta**3 + 2002710528000000000*theta**2 - 510935040000000000*theta",
        "shift": 6,
        "source": "P_6(theta-6)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "-5898240000000000*theta**9 + 123863040000000000*theta**8 - 1031651328000000000*theta**7 + 4323852288000000000*theta**6 - 9484124160000000000*theta**5 + 10007101440000000000*theta**4 - 3368681472000000000*theta**3 - 953745408000000000*theta**2 + 389283840000000000*theta",
        "shift": 7,
        "source": "P_7(theta-7)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-655360000000000*theta**9 + 18677760000000000*theta**8 - 220200960000000000*theta**7 + 1390018560000000000*theta**6 - 5078384640000000000*theta**5 + 10824253440000000000*theta**4 - 12867338240000000000*theta**3 + 7585136640000000000*theta**2 - 1651507200000000000*theta",
        "shift": 8,
        "source": "P_8(theta-8)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "27001782375529*theta**9 - 972064165519044*theta**8 + 14742973177038834*theta**7 - 122480084855399544*theta**6 + 606163012548250521*theta**5 - 1816787925355093236*theta**4 + 3189558541326987596*theta**3 - 2958963319839969936*theta**2 + 1088711865381329280*theta",
        "shift": 9,
        "source": "P_9(theta-9)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      14
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        14
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    3,
    15,
    270,
    5505,
    124818
  ],
  "status": "verified",
  "terms": [
    1,
    3,
    15,
    270,
    5505,
    124818,
    3028200,
    76896180,
    2018211930,
    54311811330,
    1490518569747,
    41556060361920,
    1173726329836125,
    33513124885393020,
    965755118941566180,
    28051840723006217040,
    820439774630057541690,
    24140990868547130110530,
    714138665690363414924445,
    21226337257333849309100430,
    633604410533167911973198980,
    18985815837632184818589581040,
    570888612740185893621644263200,
    17220620350468825066393749031500
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A244594

### Defining data

```json
{
  "equation": "(4-1*x)*A(x)=3+A(x)^3",
  "linear_coefficient_d": "1",
  "q": 3,
  "r": 4,
  "s": 1,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "rational inverse rearranged as positive recursive grammar",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_2_with_one_true_leaf_and_one_subtree": 1,
    "Delta_3": 1
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+1*x*T+3*T^2+1*T^3",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2_marked",
      "Delta_2",
      "Delta_3"
    ],
    "true_false_encoding": "full ordered slots contain subtree/true leaves or false leaves; the marked Delta_2 constructor contains one new true leaf and one recursive subtree",
    "unary_branching": "absent: x*T is represented by a genuinely binary Delta_2 node"
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 4,
      "pass": true,
      "published_term": 4
    },
    "3": {
      "enumerated": 29,
      "pass": true,
      "published_term": 29
    }
  },
  "elements_by_true_leaf_count": {
    "1": [
      "root[0](l)"
    ],
    "2": [
      "root[0](Delta_2m[0](l,l))",
      "root[0](Delta_2[0](l,l))",
      "root[0](Delta_2[1](l,l))",
      "root[0](Delta_2[2](l,l))"
    ],
    "3": [
      "root[0](Delta_2m[0](l,Delta_2m[0](l,l)))",
      "root[0](Delta_2m[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2m[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2m[0](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[0](l,Delta_2m[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2m[0](l,l)))",
      "root[0](Delta_2[2](l,Delta_2m[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[0](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[1](l,l)))",
      "root[0](Delta_2[0](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[1](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[2](l,Delta_2[2](l,l)))",
      "root[0](Delta_2[0](Delta_2m[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2m[0](l,l),l))",
      "root[0](Delta_2[2](Delta_2m[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[0](l,l),l))",
      "root[0](Delta_2[1](Delta_2[0](l,l),l))",
      "root[0](Delta_2[2](Delta_2[0](l,l),l))",
      "root[0](Delta_2[0](Delta_2[1](l,l),l))",
      "root[0](Delta_2[1](Delta_2[1](l,l),l))",
      "root[0](Delta_2[2](Delta_2[1](l,l),l))",
      "root[0](Delta_2[0](Delta_2[2](l,l),l))",
      "root[0](Delta_2[1](Delta_2[2](l,l),l))",
      "root[0](Delta_2[2](Delta_2[2](l,l),l))",
      "root[0](Delta_3[0](l,l,l))"
    ]
  },
  "encoding": "prefix depth-first Delta word; Delta_2m(l,T) is the marked binary x*T constructor",
  "maximum_true_leaves": 3,
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "E": "(1-3*u^1-1*u^2)/(1+1*u)",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n)*integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0 avoiding the other local singularities",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-1*u^2)/(1+1*u)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "direct_x_assessment": {
    "degree_in_u": 3,
    "generic_squarefree_witness": "discriminant_u(g_x)=-4*x**3 + 48*x**2 - 192*x + 13",
    "kernel": "g_x(u)=p(u)-x*h(u)=-u**3 - 3*u**2 - u*x + u - x",
    "result": "same_polynomial_algorithm",
    "route": "apply the paper's G_x/U_x/V_x derivative reduction directly to 1/g_x; this is the preferred first implementation"
  },
  "integrand": "(1)*(u + 1)^n/(n*(-u**3 - 3*u**2 + u)^n)",
  "kernel_class": "rational_rho_or_two_polynomial_hyperexponential",
  "logarithmic_u_derivative": "n*((1)/(u + 1)-(-3*u**2 - 6*u + 1)/(-u**3 - 3*u**2 + u))",
  "required_change": "implement direct-x polynomial reduction first; defer term-shift certificates until the two-factor lowering identity is derived and checked",
  "resolution": "numerator-aware direct-x reduction verified",
  "status": "verified",
  "term_shift_assessment": {
    "candidate": "two-factor Hermite reduction over poles p=0 and h=0, retaining exact n-dependent residues",
    "reason": "the numerator h^n varies with n, so the single-polynomial rho G/U/V identity does not apply unchanged",
    "result": "requires_generalization"
  },
  "term_shift_ratio": "n*(u + 1)^s/((n+s)*(-u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `runs/A244594-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices`

```json
{
  "canonical_source": "runs/A244594-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "full_entries_location": "runs/A244594-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "matrix_shapes": {
    "Gx": [
      6,
      6
    ],
    "Gx_inverse": [
      6,
      6
    ],
    "J": [
      3,
      3
    ],
    "Ux": [
      3,
      3
    ],
    "Vx": [
      3,
      3
    ],
    "X": [
      2,
      3
    ],
    "X_full": [
      3,
      3
    ],
    "embedding_E": [
      6,
      3
    ]
  },
  "pilot_statistics": {
    "Gx_determinant": "4*x**3 - 48*x**2 + 192*x - 13",
    "Gx_nonzero": 21,
    "Gx_shape": [
      6,
      6
    ],
    "X_rank": 2,
    "X_shape": [
      2,
      3
    ],
    "certificate_degree_u": 5,
    "certificate_degree_x": 3,
    "ode_for_A_prime_order": 2,
    "peak_rss_kib": 63524,
    "recurrence_order": 4,
    "wall_seconds": 1.6377752100006546
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "-4*x**2/(4*x**3 - 48*x**2 + 192*x - 13) + 32*x/(4*x**3 - 48*x**2 + 192*x - 13) - 91/(4*x**3 - 48*x**2 + 192*x - 13)",
          "-60*x**3/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 1692*x**2/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) - 10656*x/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 22308/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169)"
        ],
        [
          "1",
          "-27/(4*x**3 - 48*x**2 + 192*x - 13)",
          "-60*x**3/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 720*x**2/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) - 2880*x/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 6756/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169)"
        ]
      ],
      "shape": [
        2,
        3
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "-4*x**2/(4*x**3 - 48*x**2 + 192*x - 13) + 32*x/(4*x**3 - 48*x**2 + 192*x - 13) - 91/(4*x**3 - 48*x**2 + 192*x - 13)",
          "-60*x**3/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 1692*x**2/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) - 10656*x/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 22308/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169)"
        ],
        [
          "1",
          "-27/(4*x**3 - 48*x**2 + 192*x - 13)",
          "-60*x**3/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 720*x**2/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) - 2880*x/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169) + 6756/(16*x**6 - 384*x**5 + 3840*x**4 - 18536*x**3 + 38112*x**2 - 4992*x + 169)"
        ],
        [
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        3,
        3
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `runs/A244594-direct-x-pilot/case.json#/recurrence`

```json
[
  "4*n**3 + 2*n**2 - 2*n",
  "-64*n**3 - 168*n**2 - 136*n - 32",
  "384*n**3 + 1824*n**2 + 2848*n + 1472",
  "-781*n**3 - 5825*n**2 - 14286*n - 11520",
  "52*n**3 + 468*n**2 + 1352*n + 1248"
]
```

### Rational telescoping certificate

Canonical source: `runs/A244594-direct-x-pilot/case.json#/corrected_numerator_aware_reduction/certificate`

```json
{
  "denominator_base": "-u**3 - 3*u**2 - u*x + u - x",
  "denominator_power": 2,
  "numerator": "4*u**5*x**2 - 32*u**5*x + 64*u**5 + 20*u**4*x**2 - 160*u**4*x + 320*u**4 + 2*u**3*x**3 + 16*u**3*x**2 - 224*u**3*x + 593*u**3 + 6*u**2*x**3 - 11*u**2*x**2 - 200*u**2*x + 835*u**2 + 6*u*x**3 - 10*u*x**2 - 46*u*x + 203*u + 2*x**3 + x**2 + 58*x - 52"
}
```

### Scalar linear ODE

Canonical source: `runs/A244594-direct-x-pilot/case.json#/ode_for_A`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "0",
      "4*x**5 - 32*x**4 + 64*x**3",
      "14*x**6 - 168*x**5 + 672*x**4 - 1139*x**3",
      "4*x**7 - 64*x**6 + 384*x**5 - 781*x**4 + 52*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "4*theta**3 + 2*theta**2 - 2*theta",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-64*theta**3 + 24*theta**2 + 8*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "384*theta**3 - 480*theta**2 + 160*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-781*theta**3 + 1204*theta**2 - 423*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "52*theta**3 - 156*theta**2 + 104*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    4,
    29,
    263,
    2672
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    4,
    29,
    263,
    2672,
    29088,
    331749,
    3912660,
    47329811,
    583983656,
    7321173872,
    92990672635,
    1194113490556,
    15476763809428,
    202197552311829,
    2659975668005367,
    35205831900984144,
    468468683002725372,
    6263539340729569047,
    84103985900174324256,
    1133671250214654009000,
    15334644888206889094068,
    208084583283940292897472
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A244627

### Defining data

```json
{
  "equation": "(5-4*x)*A(x)=4+A(x)^3",
  "linear_coefficient_d": "2",
  "q": 3,
  "r": 5,
  "s": 4,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "rational inverse rearranged as positive recursive grammar",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 3,
    "Delta_2_with_one_true_leaf_and_one_subtree": 2,
    "Delta_3": 2
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(2)*T(x)",
  "recursive_equation": "T=x+2*x*T+3*T^2+2*T^3",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2_marked",
      "Delta_2",
      "Delta_3"
    ],
    "true_false_encoding": "full ordered slots contain subtree/true leaves or false leaves; the marked Delta_2 constructor contains one new true leaf and one recursive subtree",
    "unary_branching": "absent: x*T is represented by a genuinely binary Delta_2 node"
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 2,
      "pass": true,
      "published_term": 2
    },
    "2": {
      "enumerated": 10,
      "pass": true,
      "published_term": 10
    },
    "3": {
      "enumerated": 84,
      "pass": true,
      "published_term": 84
    }
  },
  "encoding": "prefix depth-first Delta word; Delta_2m(l,T) is the marked binary x*T constructor",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "bc185426dd99b6973069e32e9e3165600c906bac7ab52e8bc51f28c287154929",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 2,
      "first_five": [
        "root[0](l)",
        "root[1](l)"
      ],
      "last_five": [
        "root[0](l)",
        "root[1](l)"
      ]
    },
    "2": {
      "count": 10,
      "first_five": [
        "root[0](Delta_2m[0](l,l))",
        "root[0](Delta_2m[1](l,l))",
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))"
      ],
      "last_five": [
        "root[1](Delta_2m[0](l,l))",
        "root[1](Delta_2m[1](l,l))",
        "root[1](Delta_2[0](l,l))",
        "root[1](Delta_2[1](l,l))",
        "root[1](Delta_2[2](l,l))"
      ]
    },
    "3": {
      "count": 84,
      "first_five": [
        "root[0](Delta_2m[0](l,Delta_2m[0](l,l)))",
        "root[0](Delta_2m[1](l,Delta_2m[0](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2m[1](l,l)))",
        "root[0](Delta_2m[1](l,Delta_2m[1](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2[0](l,l)))"
      ],
      "last_five": [
        "root[1](Delta_2[0](Delta_2[2](l,l),l))",
        "root[1](Delta_2[1](Delta_2[2](l,l),l))",
        "root[1](Delta_2[2](Delta_2[2](l,l),l))",
        "root[1](Delta_3[0](l,l,l))",
        "root[1](Delta_3[1](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "E": "(1-3*u^1-2*u^2)/(1+2*u)",
  "coefficient_integral": "a(n)=(2)/(2*pi*i*n)*integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0 avoiding the other local singularities",
  "ogf_integral": "A(x)=1-(2)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-3*u^1-2*u^2)/(1+2*u)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "direct_x_assessment": {
    "degree_in_u": 3,
    "generic_squarefree_witness": "discriminant_u(g_x)=-64*x**3 + 240*x**2 - 300*x + 17",
    "kernel": "g_x(u)=p(u)-x*h(u)=-2*u**3 - 3*u**2 - 2*u*x + u - x",
    "result": "same_polynomial_algorithm",
    "route": "apply the paper's G_x/U_x/V_x derivative reduction directly to 1/g_x; this is the preferred first implementation"
  },
  "integrand": "(2)*(2*u + 1)^n/(n*(-2*u**3 - 3*u**2 + u)^n)",
  "kernel_class": "rational_rho_or_two_polynomial_hyperexponential",
  "logarithmic_u_derivative": "n*((2)/(2*u + 1)-(-6*u**2 - 6*u + 1)/(-2*u**3 - 3*u**2 + u))",
  "required_change": "implement direct-x polynomial reduction first; defer term-shift certificates until the two-factor lowering identity is derived and checked",
  "resolution": "numerator-aware direct-x reduction verified",
  "status": "verified",
  "term_shift_assessment": {
    "candidate": "two-factor Hermite reduction over poles p=0 and h=0, retaining exact n-dependent residues",
    "reason": "the numerator h^n varies with n, so the single-polynomial rho G/U/V identity does not apply unchanged",
    "result": "requires_generalization"
  },
  "term_shift_ratio": "n*(2*u + 1)^s/((n+s)*(-2*u**3 - 3*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `runs/A244627-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices`

```json
{
  "canonical_source": "runs/A244627-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "full_entries_location": "runs/A244627-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "matrix_shapes": {
    "Gx": [
      6,
      6
    ],
    "Gx_inverse": [
      6,
      6
    ],
    "J": [
      3,
      3
    ],
    "Ux": [
      3,
      3
    ],
    "Vx": [
      3,
      3
    ],
    "X": [
      2,
      3
    ],
    "X_full": [
      3,
      3
    ],
    "embedding_E": [
      6,
      3
    ]
  },
  "pilot_statistics": {
    "Gx_determinant": "256*x**3 - 960*x**2 + 1200*x - 68",
    "Gx_nonzero": 21,
    "Gx_shape": [
      6,
      6
    ],
    "X_rank": 2,
    "X_shape": [
      2,
      3
    ],
    "certificate_degree_u": 5,
    "certificate_degree_x": 3,
    "ode_for_A_prime_order": 2,
    "peak_rss_kib": 64652,
    "recurrence_order": 4,
    "wall_seconds": 1.7213678419993812
  },
  "remainder_matrices": {
    "X": {
      "entries": [
        [
          "1",
          "-64*x**2/(64*x**3 - 240*x**2 + 300*x - 17) + 160*x/(64*x**3 - 240*x**2 + 300*x - 17) - 136/(64*x**3 - 240*x**2 + 300*x - 17)",
          "-3840*x**3/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 35136*x**2/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) - 69840*x/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 45084/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289)"
        ],
        [
          "2",
          "-72/(64*x**3 - 240*x**2 + 300*x - 17)",
          "-7680*x**3/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 28800*x**2/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) - 36000*x/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 25368/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289)"
        ]
      ],
      "shape": [
        2,
        3
      ]
    },
    "X_full": {
      "entries": [
        [
          "1",
          "-64*x**2/(64*x**3 - 240*x**2 + 300*x - 17) + 160*x/(64*x**3 - 240*x**2 + 300*x - 17) - 136/(64*x**3 - 240*x**2 + 300*x - 17)",
          "-3840*x**3/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 35136*x**2/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) - 69840*x/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 45084/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289)"
        ],
        [
          "2",
          "-72/(64*x**3 - 240*x**2 + 300*x - 17)",
          "-7680*x**3/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 28800*x**2/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) - 36000*x/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289) + 25368/(4096*x**6 - 30720*x**5 + 96000*x**4 - 146176*x**3 + 98160*x**2 - 10200*x + 289)"
        ],
        [
          "0",
          "0",
          "0"
        ]
      ],
      "shape": [
        3,
        3
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `runs/A244627-direct-x-pilot/case.json#/recurrence`

```json
[
  "256*n**3 + 128*n**2 - 128*n",
  "-1280*n**3 - 3360*n**2 - 2720*n - 640",
  "2400*n**3 + 11400*n**2 + 17800*n + 9200",
  "-1568*n**3 - 11590*n**2 - 28158*n - 22500",
  "85*n**3 + 765*n**2 + 2210*n + 2040"
]
```

### Rational telescoping certificate

Canonical source: `runs/A244627-direct-x-pilot/case.json#/corrected_numerator_aware_reduction/certificate`

```json
{
  "denominator_base": "-2*u**3 - 3*u**2 - 2*u*x + u - x",
  "denominator_power": 2,
  "numerator": "1024*u**5*x**2 - 2560*u**5*x + 1600*u**5 + 2560*u**4*x**2 - 6400*u**4*x + 4000*u**4 + 512*u**3*x**3 + 640*u**3*x**2 - 4000*u**3*x + 3576*u**3 + 768*u**2*x**3 - 704*u**2*x**2 - 1840*u**2*x + 2764*u**2 + 384*u*x**3 - 224*u*x**2 - 88*u*x + 142*u + 64*x**3 + 16*x**2 + 236*x - 85"
}
```

### Scalar linear ODE

Canonical source: `runs/A244627-direct-x-pilot/case.json#/ode_for_A`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "0",
      "256*x**5 - 640*x**4 + 400*x**3",
      "896*x**6 - 3360*x**5 + 4200*x**4 - 2182*x**3",
      "256*x**7 - 1280*x**6 + 2400*x**5 - 1568*x**4 + 85*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "256*theta**3 + 128*theta**2 - 128*theta",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-1280*theta**3 + 480*theta**2 + 160*theta",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "2400*theta**3 - 3000*theta**2 + 1000*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-1568*theta**3 + 2522*theta**2 - 954*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "85*theta**3 - 255*theta**2 + 170*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    2,
    10,
    84,
    882,
    10380
  ],
  "status": "verified",
  "terms": [
    1,
    2,
    10,
    84,
    882,
    10380,
    130916,
    1729960,
    23640770,
    331357276,
    4737405356,
    68818101400,
    1012852747220,
    15070913484664,
    226340757825800,
    3426481380787024,
    52232521742541410,
    801068351764540540,
    12351730365539402076,
    191363830520437179960,
    2977487020371628279260,
    46506543204844443608552,
    728944728283361649451000,
    11461857550821480534440240
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```

## A244856

### Defining data

```json
{
  "equation": "(5-1*x)*A(x)=4+A(x)^4",
  "linear_coefficient_d": "1",
  "q": 4,
  "r": 5,
  "s": 1,
  "status": "verified"
}
```

### Geometric model

Canonical source: `data/tree_model.json`

```json
{
  "attempts": [
    {
      "approach": "rational inverse rearranged as positive recursive grammar",
      "result": "pass",
      "terms_tested": 23
    }
  ],
  "branch_multiplicities": {
    "Delta_2": 6,
    "Delta_2_with_one_true_leaf_and_one_subtree": 1,
    "Delta_3": 4,
    "Delta_4": 1
  },
  "classification": "colored_unweighted",
  "component": "tree_model",
  "normalization": "A(x)=1+(1)*T(x)",
  "recursive_equation": "T=x+1*x*T+6*T^2+4*T^3+1*T^4",
  "status": "verified",
  "word_model": {
    "alphabet": [
      "l",
      "Delta_2_marked",
      "Delta_2",
      "Delta_3",
      "Delta_4"
    ],
    "true_false_encoding": "full ordered slots contain subtree/true leaves or false leaves; the marked Delta_2 constructor contains one new true leaf and one recursive subtree",
    "unary_branching": "absent: x*T is represented by a genuinely binary Delta_2 node"
  }
}
```

### Explicit elements through three true leaves

Canonical source: `data/set_elements_n_le_3.json`

```json
{
  "checks": {
    "1": {
      "enumerated": 1,
      "pass": true,
      "published_term": 1
    },
    "2": {
      "enumerated": 7,
      "pass": true,
      "published_term": 7
    },
    "3": {
      "enumerated": 95,
      "pass": true,
      "published_term": 95
    }
  },
  "encoding": "prefix depth-first Delta word; Delta_2m(l,T) is the marked binary x*T constructor",
  "full_list_location": "data/set_elements_n_le_3.json",
  "full_object_sha256": "e6ed6bf603d59cbc8933beee9f8df0afc6f2ed05821b887683d9d24fbf32e659",
  "maximum_true_leaves": 3,
  "representative_elements": {
    "1": {
      "count": 1,
      "first_five": [
        "root[0](l)"
      ],
      "last_five": [
        "root[0](l)"
      ]
    },
    "2": {
      "count": 7,
      "first_five": [
        "root[0](Delta_2m[0](l,l))",
        "root[0](Delta_2[0](l,l))",
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))"
      ],
      "last_five": [
        "root[0](Delta_2[1](l,l))",
        "root[0](Delta_2[2](l,l))",
        "root[0](Delta_2[3](l,l))",
        "root[0](Delta_2[4](l,l))",
        "root[0](Delta_2[5](l,l))"
      ]
    },
    "3": {
      "count": 95,
      "first_five": [
        "root[0](Delta_2m[0](l,Delta_2m[0](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2[0](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2[1](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2[2](l,l)))",
        "root[0](Delta_2m[0](l,Delta_2[3](l,l)))"
      ],
      "last_five": [
        "root[0](Delta_2[5](Delta_2[5](l,l),l))",
        "root[0](Delta_3[0](l,l,l))",
        "root[0](Delta_3[1](l,l,l))",
        "root[0](Delta_3[2](l,l,l))",
        "root[0](Delta_3[3](l,l,l))"
      ]
    }
  },
  "status": "verified"
}
```

### Contour representation

Canonical source: `data/contour.json`

```json
{
  "E": "(1-6*u^1-4*u^2-1*u^3)/(1+1*u)",
  "coefficient_integral": "a(n)=(1)/(2*pi*i*n)*integral_gamma du/rho(u)^n, n>=1",
  "component": "contour",
  "contour": "small positively oriented loop around u=0 avoiding the other local singularities",
  "ogf_integral": "A(x)=1-(1)/(2*pi*i)*integral_gamma log(1-x/rho(u)) du",
  "rho": "u*(1-6*u^1-4*u^2-1*u^3)/(1+1*u)",
  "status": "verified"
}
```

### Integrand analysis

Canonical source: `data/integrand_analysis.json`

```json
{
  "direct_x_assessment": {
    "degree_in_u": 4,
    "generic_squarefree_witness": "discriminant_u(g_x)=-27*x**4 + 540*x**3 - 4050*x**2 + 13500*x - 491",
    "kernel": "g_x(u)=p(u)-x*h(u)=-u**4 - 4*u**3 - 6*u**2 - u*x + u - x",
    "result": "same_polynomial_algorithm",
    "route": "apply the paper's G_x/U_x/V_x derivative reduction directly to 1/g_x; this is the preferred first implementation"
  },
  "integrand": "(1)*(u + 1)^n/(n*(-u**4 - 4*u**3 - 6*u**2 + u)^n)",
  "kernel_class": "rational_rho_or_two_polynomial_hyperexponential",
  "logarithmic_u_derivative": "n*((1)/(u + 1)-(-4*u**3 - 12*u**2 - 12*u + 1)/(-u**4 - 4*u**3 - 6*u**2 + u))",
  "required_change": "implement direct-x polynomial reduction first; defer term-shift certificates until the two-factor lowering identity is derived and checked",
  "resolution": "numerator-aware direct-x reduction verified",
  "status": "verified",
  "term_shift_assessment": {
    "candidate": "two-factor Hermite reduction over poles p=0 and h=0, retaining exact n-dependent residues",
    "reason": "the numerator h^n varies with n, so the single-polynomial rho G/U/V identity does not apply unchanged",
    "result": "requires_generalization"
  },
  "term_shift_ratio": "n*(u + 1)^s/((n+s)*(-u**4 - 4*u**3 - 6*u**2 + u)^s)"
}
```

### Exact reduction matrices

Canonical source: `runs/A244856-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices`

```json
{
  "canonical_source": "runs/A244856-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "full_entries_location": "runs/A244856-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
  "matrix_shapes": {
    "Gx": [
      8,
      8
    ],
    "Gx_inverse": [
      8,
      8
    ],
    "J": [
      4,
      4
    ],
    "Ux": [
      4,
      4
    ],
    "Vx": [
      4,
      4
    ],
    "X": [
      3,
      4
    ],
    "X_full": [
      4,
      4
    ],
    "embedding_E": [
      8,
      4
    ]
  },
  "pilot_statistics": {
    "Gx_determinant": "-27*x**4 + 540*x**3 - 4050*x**2 + 13500*x - 491",
    "Gx_nonzero": 36,
    "Gx_shape": [
      8,
      8
    ],
    "X_rank": 3,
    "X_shape": [
      3,
      4
    ],
    "certificate_degree_u": 10,
    "certificate_degree_x": 4,
    "ode_for_A_prime_order": 3,
    "peak_rss_kib": 74560,
    "recurrence_order": 5,
    "wall_seconds": 8.18998242699945
  },
  "remainder_matrices": {
    "X": {
      "entry_count": 12,
      "full_entries_location": "runs/A244856-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
      "full_object_sha256": "a2777aabad59416c3f8be916c033e2e9cdf7ca874663bd7bab00e176b40c40be",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "-127733760*x**5/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 3193344000*x**4/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 31933440000*x**3/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 159667200000*x**2/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 430373621760*x/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 555196108800/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771)",
        "top_left": "1",
        "top_right": "320760*x**8/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 20995200*x**7/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 510300000*x**6/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 6659573760*x**5/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 54451645200*x**4/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 307086180480*x**3/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 1216428127200*x**2/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 3050927957760*x/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 3678963562680/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771)"
      },
      "shape": [
        3,
        4
      ]
    },
    "X_full": {
      "entry_count": 16,
      "full_entries_location": "runs/A244856-direct-x-pilot/case.json#/direct_reduction_base_matrices/matrices",
      "full_object_sha256": "68c6a893c585d6b0dde5590ae77371f8a73503d35ec70fb085574a85654baed4",
      "representative_entries": {
        "bottom_left": "0",
        "bottom_right": "0",
        "top_left": "1",
        "top_right": "320760*x**8/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 20995200*x**7/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 510300000*x**6/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 6659573760*x**5/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 54451645200*x**4/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 307086180480*x**3/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 1216428127200*x**2/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) - 3050927957760*x/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771) + 3678963562680/(19683*x**12 - 1180980*x**11 + 32476950*x**10 - 541282500*x**9 + 6053596317*x**8 - 47282152680*x**7 + 259091046900*x**6 - 967062969000*x**5 + 2259994250061*x**4 - 2621838101220*x**3 + 271383384150*x**2 - 9763780500*x + 118370771)"
      },
      "shape": [
        4,
        4
      ]
    }
  },
  "status": "verified"
}
```

### Polynomial recurrence

Canonical source: `release/attached_order4_certificate.json#/recurrence`

```json
{
  "minimal_order_claim": false,
  "orientation": "sum_{j=0}^4 p_j(n)*a(n+j)=0",
  "p": [
    "3*(n+1)*(3*n-1)*(3*n+7)",
    "-15*(2*n+3)*(18*n^2+54*n+29)",
    "75*(n+2)*(54*n^2+216*n+209)",
    "-6750*(n+2)*(n+3)*(2*n+5)",
    "491*(n+2)*(n+3)*(n+4)"
  ],
  "validity": "creative-telescoping proof for n>=1; n=0 checked directly"
}
```

### Rational telescoping certificate

Canonical source: `release/attached_order4_certificate.json#/certificate`

```json
{
  "C": "(1+t)*P/(n*(n+1)*t^3*Q^3)",
  "P_coefficients_by_t_power": [
    "-491*n*(n+1)*(n+2)",
    "4*n*(n+1)*(1411*n+2791)",
    "n*(11394*n^2+34382*n+23093)",
    "15004*n^3+47764*n^2+31584*n-21",
    "16447*n^3+56569*n^2+42180*n+378",
    "6*(2644*n^3+9656*n^2+7971*n-336)",
    "7*(1812*n^3+6940*n^2+6463*n+225)",
    "4*(2094*n^3+8438*n^2+9116*n+1827)",
    "4611*n^3+19393*n^2+23539*n+7812",
    "15*(132*n^3+568*n^2+730*n+287)",
    "198*(n+1)^2*(3*n+7)",
    "36*(n+1)^2*(3*n+7)",
    "3*(n+1)^2*(3*n+7)"
  ],
  "identity_reduced": "sum_j p_j(n)*R^j/(n+j) = dC/dt + n*(R'/R)*C"
}
```

### Scalar linear ODE

Canonical source: `release/attached_order4_certificate.json#/ode_from_recurrence`

```json
{
  "boundary_polynomial": "0",
  "coefficient_correspondence": {
    "formula": "[x^(n+s)](L_q A_q-B_q)=sum_r P_r(n)a_q(n+r)",
    "samples": [
      {
        "difference": "0",
        "n": 1,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 2,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 3,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 4,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 5,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 6,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 7,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 8,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 9,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 10,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 11,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 12,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 13,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 14,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 15,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      },
      {
        "difference": "0",
        "n": 16,
        "ode_coefficient": "0",
        "recurrence_residual": "0"
      }
    ]
  },
  "ordinary_derivative_form": {
    "coefficients": [
      "-21*x**4 + 105*x**3",
      "141*x**5 - 1410*x**4 + 3525*x**3",
      "162*x**6 - 2430*x**5 + 12150*x**4 - 20250*x**3",
      "27*x**7 - 540*x**6 + 4050*x**5 - 13500*x**4 + 491*x**3"
    ],
    "identity": "sum_j C_j(x) d^j A_q(x)/dx^j = B_q(x)",
    "order": 3
  },
  "series": "A_q(x)",
  "status": "complete",
  "theta_definition": "theta=x*d/dx",
  "theta_operator": {
    "identity": "L_q(x,theta)=sum_{r=0}^{s} x^(s-r) P_r(theta-r)",
    "terms": [
      {
        "polynomial_in_theta": "27*theta**3 + 81*theta**2 + 33*theta - 21",
        "shift": 0,
        "source": "P_0(theta-0)",
        "x_power": 4
      },
      {
        "polynomial_in_theta": "-540*theta**3 - 810*theta**2 - 60*theta + 105",
        "shift": 1,
        "source": "P_1(theta-1)",
        "x_power": 3
      },
      {
        "polynomial_in_theta": "4050*theta**3 - 525*theta",
        "shift": 2,
        "source": "P_2(theta-2)",
        "x_power": 2
      },
      {
        "polynomial_in_theta": "-13500*theta**3 + 20250*theta**2 - 6750*theta",
        "shift": 3,
        "source": "P_3(theta-3)",
        "x_power": 1
      },
      {
        "polynomial_in_theta": "491*theta**3 - 1473*theta**2 + 982*theta",
        "shift": 4,
        "source": "P_4(theta-4)",
        "x_power": 0
      }
    ]
  },
  "validity": {
    "safe_series_exponent_range": [
      0,
      20
    ],
    "source_recurrence_valid_from_n": 1
  },
  "verification": {
    "recurrence_coefficient_correspondence": {
      "checked_n": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16
      ],
      "max_absolute_difference": 0,
      "pass": true,
      "relation": "ODE coefficient equals recurrence residual"
    },
    "series_residual": {
      "checked_exponents": [
        0,
        20
      ],
      "max_absolute_residual": 0,
      "pass": true,
      "relation": "L_q A_q-B_q=0 coefficientwise on the safe emitted range"
    }
  }
}
```

### Exact terms and published prefix

Canonical source: `data/terms.json`

```json
{
  "oeis_prefix_checked": [
    1,
    1,
    7,
    95,
    1614,
    30718
  ],
  "status": "verified",
  "terms": [
    1,
    1,
    7,
    95,
    1614,
    30718,
    626434,
    13383650,
    295692145,
    6700461777,
    154871912815,
    3637093846055,
    86539594779772,
    2081721640140460,
    50542732376144460,
    1236960716959913020,
    30483096737455969766,
    755783491624380578998,
    18839297079646725396450,
    471851408962496233087650,
    11868704590155385681048336,
    299692001928510713998079040,
    7593867339185292554658573320,
    193032501223516068520866476120
  ]
}
```

### Verification results

Canonical source: `checks/results.json`

```json
{
  "checks": {
    "defining_equation_terms_integral": {
      "count": 24,
      "status": "pass"
    },
    "oeis_initial_terms_match": {
      "count": 6,
      "status": "pass"
    }
  },
  "status": "verified"
}
```
