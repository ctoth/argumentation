{ accepted_arg(A) } :- arg(A).

countered(A) :- accepted_arg(B), defeat(B,A).
undefended(A) :- arg(A), defeat(B,A), not countered(B).

:- accepted_arg(A), accepted_arg(B), attack(A,B).
:- accepted_arg(A), undefended(A).

#show accepted_arg/1.
