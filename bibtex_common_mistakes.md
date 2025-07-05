# Common BibTeX Mistakes and Best Practices

Here are some of the most common mistakes users make in `.bib` files and how to correct them for a clean, well-formatted bibliography.

### 1. Not Protecting Capitalization in Titles

**The Mistake:** BibTeX styles often force titles into sentence case or title case, which can incorrectly lowercase proper nouns, acronyms, or other essential capitals.

*Incorrect:*

```bibtex
title = {A study of JSON versus XML in modern web APIs},
```

**The Correction:** Wrap the specific words or the entire title in an extra set of braces `{}` to prevent the style file from changing their capitalization.

*Correct:*

```bibtex
title = {A study of {JSON} versus {XML} in modern web {APIs}},
```

*Or for the whole title:*

```bibtex
title = {{A study of JSON versus XML in modern web APIs}},
```

### 2. Missing Commas Between Fields

**The Mistake:** Forgetting a comma after a field. Each field in an entry must be separated by a comma. This is a common syntax error that will cause BibTeX to fail.

*Incorrect:*

```bibtex
@article{smith2023,
  author = {Smith, John},
  title = {My Great Paper}
  year = {2023}
}
```

**The Correction:** Ensure every field, including the one right before the closing `}`, has a comma after it. Adding a comma to the last entry is also valid and makes reordering fields easier.

*Correct:*

```bibtex
@article{smith2023,
  author = {Smith, John},
  title = {My Great Paper},
  year = {2023},
}
```

### 3. Incorrectly Separating Authors

**The Mistake:** Using commas or other separators between author names.

*Incorrect:*

```bibtex
author = {John Smith, Jane Doe, Peter Jones},
```

**The Correction:** Always use the keyword `and` to separate full author names.

*Correct:*

```bibtex
author = {John Smith and Jane Doe and Peter Jones},
```

### 4. Using the Wrong Entry Type

**The Mistake:** Defaulting to `@misc` or `@article` for everything, such as books or conference papers.

*Incorrect:*

```bibtex
@misc{jones2022,
  author = {Jones, Peter},
  title = {The Big Book of Everything},
  year = {2022},
  publisher = {Big Books Inc.}
}
```

**The Correction:** Use the most specific entry type available (`@book`, `@inproceedings`, `@phdthesis`, etc.). This ensures that the correct fields are used and the entry is formatted properly in the final document.

*Correct:*

```bibtex
@book{jones2022,
  author = {Jones, Peter},
  title = {The Big Book of Everything},
  year = {2022},
  publisher = {Big Books Inc.}
}
```

### 5. Escaping Special Characters

**The Mistake:** Using special LaTeX characters like `&`, `%`, or `$` directly in fields.

*Incorrect:*

```bibtex
title = {Profit & Loss Statements},
```

**The Correction:** Escape these characters with a backslash `\` so LaTeX interprets them correctly.

*Correct:*

```bibtex
title = {Profit \& Loss Statements},
```

```
```
