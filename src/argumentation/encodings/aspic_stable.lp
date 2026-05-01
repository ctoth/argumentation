element(P) :- premise(P).
element(R) :- d_head(R,_).

{ accepted_arg(X) } :- element(X).

derived(L) :- axiom(L).
derived(P) :- premise(P), accepted_arg(P).
derived(H) :- s_head(R,H),
    #count { B : s_body(R,B) } = #count { B : s_body(R,B), derived(B) }.
derived(H) :- d_head(R,H), accepted_arg(R),
    #count { B : d_body(R,B) } = #count { B : d_body(R,B), derived(B) }.

attacked(X) :- element(X), contrary(C,X), derived(C).

:- accepted_arg(X), attacked(X).
:- element(X), not accepted_arg(X), not attacked(X).

accepted_lit(L) :- derived(L).

#show accepted_arg/1.
#show accepted_lit/1.
