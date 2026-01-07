EYRE 1998 - UNCONDITIONALLY GRADIENT STABLE SCHEME
====================================================

D.J. Eyre (1998)
"Unconditionally gradient stable time marching the Cahn-Hilliard equation"

KEY IDEA:
- Split potential into convex + concave parts
- Treat convex part implicitly
- Treat concave part explicitly
- GUARANTEES dÎ©/dt â‰¤ 0 at discrete level!

UET uses exactly this idea (semi-implicit scheme).
