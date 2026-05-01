{ selected(A) } :- assumption(A).

derived(L) :- assumption_literal(A,L), selected(A).
derived(H) :- rule(R), head(R,H), body_count(R,N),
    N = #count { B : body(R,B), derived(B) }.

attacked(A) :- contrary(A,C), derived(C).

:- selected(A), attacked(A).
:- assumption(A), not selected(A), not attacked(A).

accepted_arg(A) :- selected(A).
#show accepted_arg/1.
