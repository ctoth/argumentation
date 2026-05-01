{ accepted_arg(A) } :- arg(A).

defeated(A) :- accepted_arg(B), defeat(B,A).

:- accepted_arg(A), accepted_arg(B), attack(A,B).
:- arg(A), not accepted_arg(A), not defeated(A).

#show accepted_arg/1.
