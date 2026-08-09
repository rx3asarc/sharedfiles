# OMB+ Cheat Sheet — Full Reference (English, LaTeX)

## 1. Basic Arithmetic

### Sign Rules
```
+ \cdot + = + \quad + \cdot - = - \quad - \cdot + = - \quad - \cdot - = +
-(-a) = a \quad -(a + b) = -a - b
```

### Fractions
```
\frac{a}{b} + \frac{c}{d} = \frac{ad + bc}{bd}
\frac{a}{b} \cdot \frac{c}{d} = \frac{ac}{bd}
\frac{a}{b} \div \frac{c}{d} = \frac{a}{b} \cdot \frac{d}{c} = \frac{ad}{bc}
```

### Binomial Formulas
```
(a + b)^2 = a^2 + 2ab + b^2
(a - b)^2 = a^2 - 2ab + b^2
(a + b)(a - b) = a^2 - b^2
```

### Powers
```
a^0 = 1 \qquad a^1 = a
a^m \cdot a^n = a^{m+n}
\frac{a^m}{a^n} = a^{m-n}
(a^m)^n = a^{m \cdot n}
a^{-n} = \frac{1}{a^n}
a^{1/n} = \sqrt[n]{a}
```

### Roots
```
\sqrt[n]{a} = a^{1/n}
\sqrt[n]{a \cdot b} = \sqrt[n]{a} \cdot \sqrt[n]{b}
\sqrt[n]{\frac{a}{b}} = \frac{\sqrt[n]{a}}{\sqrt[n]{b}}
```

### Percentages
```
p\% = \frac{p}{100}
\text{Base} \cdot \text{Rate} = \text{Value}
```

---

## 2. Equations

### Linear Equation: $ax + b = 0$
```
x = -\frac{b}{a}
```

### Quadratic Equation: $ax^2 + bx + c = 0$
```
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
D = b^2 - 4ac
D > 0 \to 2 \text{ solutions} \quad D = 0 \to 1 \text{ solution} \quad D < 0 \to \text{no real solutions}
```

### Equations with Roots
```
\text{Isolate } \sqrt{(\ldots)} \text{, then square both sides}
\text{Always check solutions! (Extraneous solutions possible)}
```

### Absolute Value Equations: $|x| = a$
```
x = a \text{ or } x = -a \quad (\text{for } a \ge 0)
```

### Substitution
```
\text{For } x^4 + ax^2 + b = 0:\ \text{set } u = x^2 \Rightarrow u^2 + au + b = 0
```

---

## 3. Inequalities

### Rules
```
\text{Addition/Subtraction: } a < b \Rightarrow a \pm c < b \pm c
\text{Multiplication by } c > 0: a < b \Rightarrow ac < bc
\text{Multiplication by } c < 0: a < b \Rightarrow ac > bc \text{ (flip!)}
```

### Absolute Value Inequalities
```
|x| < a \Rightarrow -a < x < a
|x| > a \Rightarrow x < -a \text{ or } x > a
```

---

## 4. Systems of Linear Equations

### 2 Equations, 2 Unknowns
```
\text{Substitution: solve one eqn for } x \text{, plug into the other}
\text{Elimination: multiply eqns, then add/subtract}
```

### Gaussian Elimination
```
1. \text{Write system as augmented matrix}
2. \text{Row operations (swap, multiply, add)}
3. \text{Transform to triangular form}
4. \text{Back-substitute}
```

---

## 5. Geometry

### Triangle
```
\text{Area: } A = \frac{1}{2} \cdot \text{base} \cdot \text{height}
\text{Pythagorean theorem: } a^2 + b^2 = c^2
```

### Circle
```
\text{Circumference: } C = 2\pi r
\text{Area: } A = \pi r^2
```

### Volume
```
\text{Rectangular box: } V = l \cdot w \cdot h
\text{Sphere: } V = \frac{4}{3}\pi r^3
\text{Cylinder: } V = \pi r^2 h
\text{Cone: } V = \frac{1}{3}\pi r^2 h
```

---

## 6. Elementary Functions

### Properties
```
\text{Zeros: } f(x) = 0
\text{Symmetry: } f(-x) = f(x) \to \text{even}; \quad f(-x) = -f(x) \to \text{odd}
\text{Monotonicity: } f'(x) > 0 \to \text{increasing}; \quad f'(x) < 0 \to \text{decreasing}
```

### Power Functions: $f(x) = x^n$
```
n \text{ even } \to \text{parabola shape}, \quad n \text{ odd } \to \text{S-shape}
```

### Exponential Functions: $f(x) = a^x$ $(a > 0, a \neq 1)$
```
a^0 = 1, \quad a^1 = a
```

### Logarithmic Functions: $\log_a(x) = y \iff a^y = x$
```
\ln(x) = \log_e(x)
\log(a \cdot b) = \log(a) + \log(b)
\log\left(\frac{a}{b}\right) = \log(a) - \log(b)
\log(a^n) = n \cdot \log(a)
```

### Trigonometric Functions
```
\sin^2(x) + \cos^2(x) = 1
\sin(0)=0,\ \sin(\pi/2)=1,\ \cos(0)=1,\ \cos(\pi/2)=0
\text{Period: } \sin, \cos \to 2\pi;\ \tan \to \pi
```

### Transformations
```
f(x) + c \to \text{shift up}
f(x + c) \to \text{shift left}
c \cdot f(x) \to \text{stretch vertically}
f(c \cdot x) \to \text{compress horizontally}
-f(x) \to \text{reflect across x-axis}
f(-x) \to \text{reflect across y-axis}
```

---

## 7. Differential Calculus

### Limits
```
\lim_{x \to a} f(x) = L
\lim_{x \to \infty} \frac{1}{x} = 0
```

### Basic Derivatives
```
f(x) = c          \Rightarrow f'(x) = 0
f(x) = x^n        \Rightarrow f'(x) = n \cdot x^{n-1}
f(x) = e^x        \Rightarrow f'(x) = e^x
f(x) = \ln(x)     \Rightarrow f'(x) = \frac{1}{x}
f(x) = \sin(x)    \Rightarrow f'(x) = \cos(x)
f(x) = \cos(x)    \Rightarrow f'(x) = -\sin(x)
```

### Differentiation Rules
```
\text{Sum: } (u+v)' = u' + v'
\text{Constant factor: } (c \cdot u)' = c \cdot u'
\text{Product: } (u \cdot v)' = u' \cdot v + u \cdot v'
\text{Quotient: } \left(\frac{u}{v}\right)' = \frac{u' \cdot v - u \cdot v'}{v^2}
\text{Chain: } (u(v(x)))' = u'(v(x)) \cdot v'(x)
```

### Extrema
```
\text{Necessary: } f'(x) = 0
\text{Sufficient: } f''(x) < 0 \to \text{maximum}; \quad f''(x) > 0 \to \text{minimum}
```

### Inflection Points
```
f''(x) = 0 \text{ and } f'''(x) \neq 0
```

---

## 8. Integral Calculus

### Basic Integrals
```
\int x^n \,dx = \frac{x^{n+1}}{n+1} + C \quad (n \neq -1)
\int \frac{1}{x} \,dx = \ln|x| + C
\int e^x \,dx = e^x + C
\int \sin(x) \,dx = -\cos(x) + C
\int \cos(x) \,dx = \sin(x) + C
```

### Definite Integral
```
\int_a^b f(x)\,dx = F(b) - F(a) \quad \text{(Fundamental Theorem)}
```

### Area Between Curve and x-axis
```
A = \int_a^b |f(x)|\,dx
```

### Area Between Two Curves
```
A = \int_a^b |f(x) - g(x)|\,dx
```

---

## 9. 2D Coordinate System

### Line Equations
```
\text{Slope-intercept: } y = mx + b
\text{General: } ax + by = c
\text{Point-slope: } y - y_1 = m(x - x_1)
```

### Slope
```
m = \frac{y_2 - y_1}{x_2 - x_1}
```

### Circle: Center $(h,k)$, radius $r$
```
(x - h)^2 + (y - k)^2 = r^2
```

---

## 10. Vector Geometry

### Vector Operations
```
\text{Addition: } (x_1,y_1,z_1) + (x_2,y_2,z_2) = (x_1+x_2,\ y_1+y_2,\ z_1+z_2)
\text{Scalar mult: } c \cdot (x,y,z) = (cx,\ cy,\ cz)
```

### Dot Product
```
\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos(\theta) = a_1b_1 + a_2b_2 + a_3b_3
\mathbf{a} \cdot \mathbf{b} = 0 \to \text{perpendicular}
```

### Cross Product (3D)
```
\mathbf{a} \times \mathbf{b} = (a_2b_3 - a_3b_2,\ a_3b_1 - a_1b_3,\ a_1b_2 - a_2b_1)
\mathbf{a} \times \mathbf{b} \text{ is perpendicular to both } \mathbf{a} \text{ and } \mathbf{b}
```

### Magnitude (Length)
```
|\mathbf{a}| = \sqrt{a_1^2 + a_2^2 + a_3^2}
```

### Line in 3D
```
\mathbf{g}: \mathbf{x} = \mathbf{p} + t\mathbf{v}
(\mathbf{p} = \text{position vector}, \mathbf{v} = \text{direction vector})
```

### Plane in 3D
```
\text{Parametric: } \mathbf{x} = \mathbf{p} + t\mathbf{u} + s\mathbf{v}
\text{Normal form: } \mathbf{n} \cdot (\mathbf{x} - \mathbf{p}) = 0
```

---

## Useful Constants

```
\pi \approx 3.14159
e \approx 2.71828
\sqrt{2} \approx 1.414
\sqrt{3} \approx 1.732
```