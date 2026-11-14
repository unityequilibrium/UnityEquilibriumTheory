# Limitations

- The primary verifier uses the standard Rydberg relation with CODATA `R_H`; it does not derive `R_H` from UET first principles.
- The current benchmark covers selected hydrogen Balmer and Lyman lines only.
- Local spectral rows may be rounded or curated; source-table transcription precision should be audited before public ppm claims.
- Air wavelengths are present in the data but the primary metric uses vacuum wavelengths only.
- The engine has a local rounded `R_H = 1.09677e7 m^-1`; ppm-level claims should use the CODATA working copy instead.
- The three-body script is a coupling smoke test and does not validate atomic three-body physics.
- Fine structure, Lamb shift, hyperfine structure, helium, and many-electron atoms are outside the current artifact.
- Downstream core topics must inherit these limitations before using `0.20` as atomic evidence.
