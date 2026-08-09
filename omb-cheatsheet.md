# OMB+ Cheat Sheet — Full Reference

## 1. Elementares Rechnen

### Vorzeichenregeln
```
+ · + = +        + · − = −        − · + = −        − · − = +
−(−a) = a        −(a + b) = −a − b
```

### Brüche
```
a/b + c/d = (ad + bc)/(bd)        a/b · c/d = (ac)/(bd)
a/b ÷ c/d = (a/b) · (d/c) = ad/(bc)
```

### Binomische Formeln
```
(a + b)² = a² + 2ab + b²
(a − b)² = a² − 2ab + b²
(a + b)(a − b) = a² − b²
```

### Potenzen
```
a⁰ = 1            a¹ = a
a^m · a^n = a^{m+n}
a^m / a^n = a^{m-n}
(a^m)^n = a^{m·n}
a^{-n} = 1/a^n
a^{1/n} = ⁿ√a
```

### Wurzeln
```
ⁿ√a = a^{1/n}
ⁿ√(a·b) = ⁿ√a · ⁿ√b
ⁿ√(a/b) = ⁿ√a / ⁿ√b
```

### Prozent
```
p% = p/100
Grundwert · Prozentsatz = Prozentwert
```

---

## 2. Gleichungen

### Lineare Gleichung: ax + b = 0
```
x = -b/a
```

### Quadratische Gleichung: ax² + bx + c = 0
```
x = [−b ± √(b² − 4ac)] / (2a)
D = b² − 4ac
D > 0 → 2 Lösungen    D = 0 → 1 Lösung    D < 0 → keine reelle Lösung
```

### Wurzelgleichungen
```
√(...) isolieren, dann quadrieren
Probe nicht vergessen! (Scheinlösungen möglich)
```

### Betragsgleichungen: |x| = a
```
x = a  oder  x = −a  (für a ≥ 0)
```

### Substitution
```
Bei x⁴ + ax² + b = 0:  setze u = x² → u² + au + b = 0
```

---

## 3. Ungleichungen

### Rechenregeln
```
Addition/Subtraktion:  a < b → a ± c < b ± c
Multiplikation mit c > 0:  a < b → ac < bc
Multiplikation mit c < 0:  a < b → ac > bc  (umdrehen!)
```

### Betragsungleichungen
```
|x| < a  →  −a < x < a
|x| > a  →  x < −a  oder  x > a
```

---

## 4. Lineare Gleichungssysteme

### 2 Gleichungen, 2 Unbekannte
```
Einsetzungsverfahren: eine Gleichung nach x umstellen, in andere einsetzen
Additionsverfahren: Gleichungen addieren nach Multiplikation mit passendem Faktor
```

### Gauß-Verfahren
```
1. System als Matrix schreiben
2. Zeilenoperationen (vertauschen, multiplizieren, addieren)
3. Auf Dreiecksform bringen
4. Rückwärtseinsetzen
```

---

## 5. Geometrie

### Dreieck
```
Fläche: A = (1/2) · g · h
Satz des Pythagoras: a² + b² = c²
```

### Kreis
```
Umfang: U = 2πr
Fläche: A = πr²
```

### Volumen
```
Quader: V = l · b · h
Kugel: V = (4/3)πr³
Zylinder: V = πr²h
Kegel: V = (1/3)πr²h
```

---

## 6. Elementare Funktionen

### Eigenschaften
```
Nullstellen: f(x) = 0
Symmetrie: f(−x) = f(x) → gerade; f(−x) = −f(x) → ungerade
Monotonie: f'(x) > 0 → steigend; f'(x) < 0 → fallend
```

### Potenzfunktionen
```
f(x) = x^n
n gerade → Parabel, n ungerade → S-förmig
```

### Exponentialfunktionen
```
f(x) = a^x  (a > 0, a ≠ 1)
a^0 = 1,  a^1 = a
```

### Logarithmusfunktionen
```
log_a(x) = y  ↔  a^y = x
ln(x) = log_e(x)
log(a·b) = log(a) + log(b)
log(a/b) = log(a) − log(b)
log(a^n) = n · log(a)
```

### Trigonometrische Funktionen
```
sin²(x) + cos²(x) = 1
sin(0)=0, sin(π/2)=1, cos(0)=1, cos(π/2)=0
Periode: sin, cos → 2π; tan → π
```

### Transformationen
```
f(x) + c → verschiebung nach oben
f(x + c) → verschiebung nach links
c·f(x) → streckung in y-Richtung
f(c·x) → stauchung in x-Richtung
−f(x) → spiegelung an x-Achse
f(−x) → spiegelung an y-Achse
```

---

## 7. Differentialrechnung

### Grenzwerte
```
lim_{x→a} f(x) = L
lim_{x→∞} 1/x = 0
```

### Ableitungen grundlegend
```
f(x) = c          → f'(x) = 0
f(x) = x^n        → f'(x) = n·x^{n-1}
f(x) = e^x        → f'(x) = e^x
f(x) = ln(x)      → f'(x) = 1/x
f(x) = sin(x)     → f'(x) = cos(x)
f(x) = cos(x)     → f'(x) = −sin(x)
```

### Ableitungsregeln
```
Summenregel: (u+v)' = u' + v'
Faktorregel: (c·u)' = c·u'
Produktregel: (u·v)' = u'·v + u·v'
Quotientenregel: (u/v)' = (u'·v − u·v') / v²
Kettenregel: (u(v(x)))' = u'(v(x)) · v'(x)
```

### Extremstellen
```
Notwendig: f'(x) = 0
Hinreichend: f''(x) < 0 → Maximum; f''(x) > 0 → Minimum
```

### Wendepunkte
```
f''(x) = 0  und  f'''(x) ≠ 0
```

---

## 8. Integralrechnung

### Grundlegende Integrale
```
∫ x^n dx = x^{n+1}/(n+1) + C  (n ≠ −1)
∫ 1/x dx = ln|x| + C
∫ e^x dx = e^x + C
∫ sin(x) dx = −cos(x) + C
∫ cos(x) dx = sin(x) + C
```

### Bestimmtes Integral
```
∫_a^b f(x) dx = F(b) − F(a)  (Hauptsatz)
```

### Fläche zwischen Kurve und x-Achse
```
A = ∫_a^b |f(x)| dx
```

### Fläche zwischen zwei Kurven
```
A = ∫_a^b |f(x) − g(x)| dx
```

---

## 9. 2D Koordinatensystem

### Geradengleichungen
```
Normalform: y = mx + b
Allgemein: ax + by = c
Punkt-Steigung: y − y₁ = m(x − x₁)
```

### Steigung
```
m = (y₂ − y₁) / (x₂ − x₁)
```

### Kreis
```
Mittelpunkt (h,k), Radius r:
(x − h)² + (y − k)² = r²
```

---

## 10. Vektorgeometrie

### Vektoroperationen
```
Addition: (x₁,y₁,z₁) + (x₂,y₂,z₂) = (x₁+x₂, y₁+y₂, z₁+z₂)
Skalarmultiplikation: c·(x,y,z) = (cx, cy, cz)
```

### Skalarprodukt
```
a · b = |a||b|cos(θ) = a₁b₁ + a₂b₂ + a₃b₃
a · b = 0 → senkrecht
```

### Kreuzprodukt (3D)
```
a × b = (a₂b₃−a₃b₂, a₃b₁−a₁b₃, a₁b₂−a₂b₁)
a × b steht senkrecht auf a und b
```

### Betrag (Länge)
```
|a| = √(a₁² + a₂² + a₃²)
```

### Gerade im Raum
```
g: x = p + t·v  (p = Stützvektor, v = Richtungsvektor)
```

### Ebene im Raum
```
Parameterform: x = p + t·u + s·v
Normalenform: n·(x − p) = 0
```

---

## Nützliche Konstanten

```
π ≈ 3.14159
e ≈ 2.71828
√2 ≈ 1.414
√3 ≈ 1.732
```