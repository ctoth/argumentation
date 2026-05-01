{ selected(A) } :- assumption(A).

derived(L) :- assumption_literal(A,L), selected(A).
derived(H) :- rule(R), head(R,H), body_count(R,N),
    N = #count { B : body(R,B), derived(B) }.

attacked(A) :- contrary(A,C), derived(C).
support_countered(S) :- support_member(S,A), attacked(A).
undefended(A) :- contrary(A,C), support_concludes(S,C), not support_countered(S).

:- selected(A), attacked(A).
:- selected(A), undefended(A).

accepted_arg(A) :- selected(A).
#show accepted_arg/1.
