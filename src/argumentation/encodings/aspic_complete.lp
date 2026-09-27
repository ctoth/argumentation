element(P) :- premise(P).
element(R) :- d_head(R,_).

{ accepted_arg(X) } :- element(X).

derived(L) :- axiom(L).
derived(P) :- premise(P), accepted_arg(P).
derived(H) :- s_head(R,H), s_body_count(R,N),
    N = #count { B : s_body(R,B), derived(B) }.
derived(H) :- d_head(R,H), accepted_arg(R), d_body_count(R,N),
    N = #count { B : d_body(R,B), derived(B) }.

% Lehtonen et al. 2020, Def 10: an element is attacked through itself
% (premise or rule name) or, for a defeasible rule, through its head.
target(X,X) :- element(X).
target(R,H) :- d_head(R,H).

attacked(X) :- target(X,T), contrary(C,T), derived(C).
support_countered(S) :- support_member(S,X), attacked(X).
undefended(X) :- target(X,T), contrary(C,T), support_concludes(S,C), not support_countered(S).

:- accepted_arg(X), attacked(X).
:- accepted_arg(X), undefended(X).
:- element(X), not accepted_arg(X), not undefended(X).

accepted_lit(L) :- derived(L).

#show accepted_arg/1.
#show accepted_lit/1.
