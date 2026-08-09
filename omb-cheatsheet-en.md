# OMB+ Cheat Sheet — Full Reference (English)

## 1. Basic Arithmetic

### Sign Rules
```
+ · + = +        + · − = −        − · + = −        − · − = +
−(−a) = a        −(a + b) = −a − b
```

### Fractions
```
a/b + c/d = (ad + bc)/(bd)        a/b · c/d = (ac)/(bd)
a/b ÷ c/d = (a/b) · (d/c) = ad/(bc)
```

### Binomial Formulas
```
(a + b)² = a² + 2ab + b²
(a − b)² = a² − 2ab + b²
(a + b)(a − b) = a² − b²
```

### Powers
```
a⁰ = 1            a¹ = a
a^m · a^n = a^{m+n}
a^m / a^n = a^{m-n}
(a^m)^n = a^{m·n}
a^{-n} = 1/a^n
a^{1/n} = ⁿ√a
```

### Roots
```
ⁿ√a = a^{1/n}
ⁿ√(a·b) = ⁿ√a · ⁿ√b
ⁿ√(a/b) = ⁿ√a / ⁿ√b
```

### Percentages
```
p% = p/100
Base · Percentage rate = Percentage value
```

---

## 2. Equations

### Linear Equation: ax + b = 0
```
x = -b/a
```

### Quadratic Equation: ax² + bx + c = 0
```
x = [−b ± √(b² − 4ac)] / (2a)
D = b² − 4ac
D > 0 → 2 solutions    D = 0 → 1 solution    D < 0 → no real solutions
```

### Equations with Roots
```
Isolate √(...), then square both sides
Always check your solutions! (Extraneous solutions possible)
```

### Absolute Value Equations: |x| = a
```
x = a  or  x = −a  (for a ≥ 0)
```

### Substitution
```
For x⁴ + ax² + b = 0:  set u = x² → u² + au + b = 0
```

---

## 3. Inequalities

### Rules
```
Addition/Subtraction:  a < b → a ± c < b ± c
Multiplication by c > 0:  a < b → ac < bc
Multiplication by c < 0:  a < b → ac > bc  (flip sign!)
```

### Absolute Value Inequalities
```
|x| < a  →  −a < x < a
|x| > a  →  x < −a  or  x > a
```

---

## 4. Systems of Linear Equations

### 2 Equations, 2 Unknowns
```
Substitution: solve one equation for x, plug into the other
Elimination: multiply equations by factors, then add/subtract
```

### Gaussian Elimination
```
1. Write system as augmented matrix
2. Row operations (swap, multiply, add)
3. Transform to triangular form
4. Back-substitute
```

---

## 5. Geometry

### Triangle
```
Area: A = (1/2) · base · height
Pythagorean theorem: a² + b² = c²
```

### Circle
```
Circumference: C = 2πr
Area: A = πr²
```

### Volume
```
Rectangular box: V = l · w · h
Sphere: V = (4/3)πr³
Cylinder: V = πr²h
Cone: V = (1/3)πr²h
```

---

## 6. Elementary Functions

### Properties
```
Zeros: f(x) = 0
Symmetry: f(−x) = f(x) → even; f(−x) = −f(x) → odd
Monotonicity: f'(x) > 0 → increasing; f'(x) < 0 → decreasing
```

### Power Functions
```
f(x) = x^n
n even → parabola shape, n odd → S-shape
```

### Exponential Functions
```
f(x) = a^x  (a > 0, a ≠ 1)
a^0 = 1,  a^1 = a
```

### Logarithmic Functions
```
log_a(x) = y  ↔  a^y = x
ln(x) = log_e(x)
log(a·b) = log(a) + log(b)
log(a/b) = log(a) − log(b)
log(a^n) = n · log(a)
```

### Trigonometric Functions
```
sin²(x) + cos²(x) = 1
sin(0)=0, sin(π/2)=1, cos(0)=1, cos(π/2)=0
Period: sin, cos → 2π; tan → π
```

### Transformations
```
f(x) + c → shift up
f(x + c) → shift left
c·f(x) → stretch vertically
f(c·x) → compress horizontally
−f(x) → reflect across x-axis
f(−x) → reflect across y-axis
```

---

## 7. Differential Calculus

### Limits
```
lim_{x→a} f(x) = L
lim_{x→∞} 1/x = 0
```

### Basic Derivatives
```
f(x) = c          → f'(x) = 0
f(x) = x^n        → f'(x) = n·x^{n-1}
f(x) = e^x        → f'(x) = e^x
f(x) = ln(x)      → f'(x) = 1/x
f(x) = sin(x)     → f'(x) = cos(x)
f(x) = cos(x)     → f'(x) = −sin(x)
```

### Differentiation Rules
```
Sum rule: (u+v)' = u' + v'
Constant factor: (c·u)' = c·u'
Product rule: (u·v)' = u'·v + u·v'
Quotient rule: (u/v)' = (u'·v − u·v') / v²
Chain rule: (u(v(x)))' = u'(v(x)) · v'(x)
```

### Extrema
```
Necessary: f'(x) = 0
Sufficient: f''(x) < 0 → maximum; f''(x) > 0 → minimum
```

### Inflection Points
```
f''(x) = 0  and  f'''(x) ≠ 0
```

---

## 8. Integral Calculus

### Basic Integrals
```
∫ x^n dx = x^{n+1}/(n+1) + C  (n ≠ −1)
∫ 1/x dx = ln|x| + C
∫ e^x dx = e^x + C
∫ sin(x) dx = −cos(x) + C
∫ cos(x) dx = sin(x) + C
```

### Definite Integral
```
∫_a^b f(x) dx = F(b) − F(a)  (Fundamental Theorem)
```

### Area Between Curve and x-axis
```
A = ∫_a^b |f(x)| dx
```

### Area Between Two Curves
```
A = ∫_a^b |f(x) − g(x)| dx
```

---

## 9. 2D Coordinate System

### Line Equations
```
Slope-intercept: y = mx + b
General form: ax + by = c
Point-slope: y − y₁ = m(x − x₁)
```

### Slope
```
m = (y₂ − y₁) / (x₂ − x₁)
```

### Circle
```
Center (h,k), radius r:
(x − h)² + (y − k)² = r²
```

---

## 10. Vector Geometry

### Vector Operations
```
Addition: (x₁,y₁,z₁) + (x₂,y₂,z₂) = (x₁+x₂, y₁+y₂, z₁+z₂)
Scalar multiplication: c·(x,y,z) = (cx, cy, cz)
```

### Dot Product
```
a · b = |a||b|cos(θ) = a₁b₁ + a₂b₂ + a₃b₃
a · b = 0 → perpendicular
```

### Cross Product (3D)
```
a × b = (a₂b₃−a₃b₂, a₃b₁−a₁b₃, a₁b₂−a₂b₁)
a × b is perpendicular to both a and b
```

### Magnitude (Length)
```
|a| = √(a₁² + a₂² + a₃²)
```

### Line in 3D
```
g: x = p + t·v  (p = position vector, v = direction vector)
```

### Plane in 3D
```
Parametric: x = p + t·u + s·v
Normal form: n·(x − p) = 0
```

---

## Useful Constants

```
π ≈ 3.14159
e ≈ 2.71828
√2 ≈ 1.414
√3 ≈ 1.732
```