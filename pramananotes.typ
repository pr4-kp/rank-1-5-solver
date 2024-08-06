/*
 * To load into a document, put 
 * "#import "pramananotes.typ": *" at the top 
 * 
 * Then under that put the following: 
 * 
 * #show: doc => style(
 *   title: "YOUR TITLE HERE", 
 *   author: "YOUR NAME", 
 *   toc: true, // set if you want table of contents
 *   doc,
 * )
 */

// put packages at the top as needed
#import "@preview/ctheorems:1.1.2": *
#import "@preview/commute:0.2.0": node, arr, commutative-diagram

// put set and show commands here; this initially sets settings 
// for the document
#let style(title: none, author: "", toc: false, doc,) = {
  show: thmrules

  // some doc settings 
  set document(title: title)
  set text(size: 10pt, font: "TeX Gyre Pagella")
  set page(margin: 1.5in)
  set heading(numbering: "1.1.1 ")

  // title, name, and date at the top of doc
  align(center, text(18pt, title)
  + linebreak() + text(15pt, author) 
  + linebreak() 
  + datetime.today().display())

  // colored links
  show link: set text(fill: rgb(0, 0, 255))

  // adds table of contents if you have toc = true 
  if toc {
    // bold & colored sections
    show outline.entry: it => {
      text(fill: rgb(0, 0, 255), it)
    }
    show outline.entry.where(level: 1): it => {
      strong(it)
    }

    outline(title: "Table of Contents", indent: auto)
  }

  // i like square matrices, you can remove this if you want
  set math.mat(delim: "[")

  doc
}

// #let defines macros for the document 
// Theorem settings
#let thmbox = thmbox.with(
  separator: [#h(0.1em)*.*#h(0.2em)],
  inset: (left: 0em, right: 0em)
)
#let thmproof = thmproof.with(
  separator: [#h(0.1em)*.*#h(0.2em)],
  inset: (left: 0em, right: 0em)
)

#let definition = thmbox("definition", "Definition")
#let problem = thmbox("problem", "Problem")
#let theorem = thmbox("theorem", "Theorem")
#let proposition = thmbox("proposition", "Proposition")
#let claim = thmbox("claim", "Claim")
#let example = thmbox("example", "Example")
#let remark = thmbox("remark", "Remark")

#let proof = thmproof("proof", "Proof")
#let soln = thmproof("soln", "Solution")

// Misc. math definitions 
#let Re = "Re"                // Real part 
#let Im = "Im"                // Imaginary part 
#let GL = "GL"                
#let dd = $upright("d")$            
#let SL = "SL"                
#let iso = $tilde.equiv$      // "isomorphic to"
#let sim = $tilde.op$
#let wedge = $and$            // wedge product
#let racts = $arrow.cw.half$  // right action 

// colorful stuff
#let vocab(term, color: fuchsia) = { text(color, box[*#term*]) }
#let todo(task) = { box(fill: orange, inset: 3pt, "TODO: " + [#task] ) }
#let hl(phrase) = { box(fill: yellow, inset: 3pt, [#phrase] ) }
