# Pylint-raportti
```
************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:25:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:31:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:41:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:53:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:81:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:93:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:104:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:104:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:131:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:145:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:145:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:163:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:169:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:189:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:189:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:220:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:220:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:264:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:282:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:282:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:307:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:307:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:334:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 8.96/10 (previous run: 8.96/10, +0.00)


************* Module queries
queries.py:1:0: C0114: Missing module docstring (missing-module-docstring)
queries.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:20:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:25:0: C0115: Missing class docstring (missing-class-docstring)
queries.py:32:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:52:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:72:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:78:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:94:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:99:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:106:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:116:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:127:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:134:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:143:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:146:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:149:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:153:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:160:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:167:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:190:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:218:0: C0116: Missing function or method docstring (missing-function-docstring)
queries.py:243:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 8.36/10 (previous run: 8.36/10, +0.00)


************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)

------------------------------------------------------------------
Your code has been rated at 0.00/10 (previous run: 0.00/10, +0.00)


************* Module seed
seed.py:1:0: C0114: Missing module docstring (missing-module-docstring)
seed.py:6:0: C0116: Missing function or method docstring (missing-function-docstring)
seed.py:9:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 9.57/10 (previous run: 9.29/10, +0.29)

```

## Docstring
Nämä ilmoitukset ovat tyyliä missing-module-docstring tai missing-function-docstring
```
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
```
Olen päättänyt, etten käytä docstringejä funktioissa tässä projektissa.

## Mahdolliset puuttuvat palautusarvot

```
app.py:104:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:145:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:189:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:220:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:282:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:307:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
```
Näissä kaikissa kohdissa on funktio, joka on tehty @app.route dekoraattorilla käyttäen `methods=["GET", "POST"]` ja lisäksi funktioissa on haarat molemmille vaihtoehdoille, joten ei ole mahdollista, että funktio ei menisi jompaankumpaan haaraan joka palauttaa.
```
@app.route("/jotain", methods=["GET", "POST"])
def joku()
    if request.method == "GET":
        return jotain
    if request.method == "POST":
        return jotain
```
