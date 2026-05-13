% Module pi_com -- finding complete assumption sets for flat ABA.
% Transcribed verbatim from Lehtonen, Wallner, Jaervisalo, TPLP 2021
% (arXiv:2108.04192), Listing 1 ("Module pi_com"). Used by the incremental
% CEGAR loop of Algorithm 1 (skeptical acceptance under preferred). Expects the
% ABA(F) facts assumption/1, head/2, body/2, contrary/2 (a subset of what
% argumentation.aba_asp.encode_aba_theory emits).
%
% An answer set I of ABA(F) cup pi_com has {a : in(a) in I} a complete
% assumption set of F, supported(x) in I iff x is forward-derivable from it, and
% out(I) the assumptions not in in(I).

in(X) :- assumption(X), not out(X).
out(X) :- assumption(X), not in(X).

supported(X) :- assumption(X), in(X).
supported(X) :- head(R,X), triggered_by_in(R).
triggered_by_in(R) :- head(R,_), supported(X) : body(R,X).

:- in(X), contrary(X,Y), supported(Y).

defeated(X) :- supported(Y), contrary(X,Y).
derived_from_undefeated(X) :- assumption(X), not defeated(X).
derived_from_undefeated(X) :- head(R,X), triggered_by_undefeated(R).
triggered_by_undefeated(R) :- head(R,_), derived_from_undefeated(X) : body(R,X).
attacked_by_undefeated(X) :- contrary(X,Y), derived_from_undefeated(Y).

:- in(X), attacked_by_undefeated(X).
:- out(X), not attacked_by_undefeated(X).

#show in/1.
#show supported/1.
