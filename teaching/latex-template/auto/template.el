(TeX-add-style-hook "template"
 (function
  (lambda ()
    (LaTeX-add-bibliographies
     "bib")
    (LaTeX-add-labels
     "sec:introduction"
     "sec:relwork"
     "sec:model"
     "fig:example"
     "sec:latex"
     "sec:concl")
    (TeX-add-symbols
     "teilnehmer"
     "ausarbeitung")
    (TeX-run-style-hooks
     "fancyhdr"
     "graphicx"
     "geometry"
     "url"
     "times"
     "latex2e"
     "art12"
     "article"
     "12pt"
     "twoside"
     "doublepage"))))

