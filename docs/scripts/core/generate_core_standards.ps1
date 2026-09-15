$specs = @(
  [ordered]@{Name='0.0_Grand_Unification'; Problem='This topic studies whether UET can act as a coherent cross-domain synthesis across the repository''s foundational theory claims.'; Variables='omega-like state variables, kappa-like coupling terms, entropy-style quantities, and cross-scale linking terms'; Assumptions='The topic relies on symbolic reasoning and cross-topic consistency rather than a single empirical benchmark pipeline.'; Domain='Internal synthesis, symbolic consistency checks, and integration of claims from subordinate topics.'; Excluded='A full empirical closure across all downstream topics or a final unified physical theory.'; Parameter='This topic inherits assumptions and calibration choices from subordinate topics and should not be described as parameter-free.'; Baseline='Cross-topic consistency against the current repository inventory and cited subordinate benchmarks.'; Metrics='symbolic consistency diagnostics, script-completion checks, and explicit mismatch logging'; Limitation='No canonical topic-local dataset currently exists, so the topic cannot be treated as a data-backed benchmark.'},
  [ordered]@{Name='0.2_Black_Hole_Physics'; Problem='This topic studies whether UET-style black-hole and sink-field models can reproduce selected black-hole observables and imaging-related benchmarks.'; Variables='black-hole mass, radius, horizon-scale quantities, sink strength, and imaging residual terms'; Assumptions='The topic uses effective modeling against selected observational references rather than a first-principles quantum-gravity derivation.'; Domain='Internal benchmark comparisons on selected black-hole catalog and imaging-style observables.'; Excluded='A full replacement of general relativity or a complete singularity-resolution proof for all regimes.'; Parameter='Boundary-condition choices and calibration terms remain important in several scripts.'; Baseline='Topic-local black-hole catalog files and cited observational comparison targets.'; Metrics='relative error on mass-radius style observables and residual mismatch against selected references'; Limitation='Any agreement here should be treated as exploratory black-hole benchmarking, not theorem-level closure.'},
  [ordered]@{Name='0.4_Superconductivity_Superfluids'; Problem='This topic studies whether UET-style condensate and pairing ideas can reproduce selected superconducting or superfluid benchmark behavior.'; Variables='critical temperature, order-parameter-like quantities, coupling terms, and material descriptors'; Assumptions='The current scripts behave like phenomenological internal models tied to selected materials and curated datasets.'; Domain='Selected superconducting materials, hydrides, and related transition benchmarks.'; Excluded='A microscopic many-body derivation for all superconductors or a universal superfluid theory.'; Parameter='Material selection and calibration choices still affect reported fits.'; Baseline='Supercon working files, calibrated superconducting datasets, and cited material references.'; Metrics='relative error on transition-temperature or materials-response benchmarks'; Limitation='The topic still needs a clear separation between phenomenological fit behavior and stronger microscopic claims.'},
  [ordered]@{Name='0.5_Nuclear_Binding_Hadrons'; Problem='This topic studies whether UET-inspired overlap and confinement models can reproduce selected nuclear-binding and hadron-related benchmarks.'; Variables='binding energy, hadron mass, confinement-scale terms, overlap parameters, and radius observables'; Assumptions='The current package mixes effective modeling, benchmark comparison, and proof-oriented language across multiple sub-scripts.'; Domain='Selected isotopes, hadron-mass comparisons, proton-radius checks, and strong-force benchmark tests.'; Excluded='A full derivation of QCD from first principles or a general confinement proof.'; Parameter='Several scripts appear calibration-aware, so public summaries must not present the topic as fully parameter-free.'; Baseline='AME2020, PDG-derived topic files, proton-radius references, and topic-local competitor scripts.'; Metrics='binding-energy residuals, selected radius residuals, and mismatch against competitor baselines'; Limitation='The topic is still exposed to claim-risk because proof language outran the current verification package.'},
  [ordered]@{Name='0.6_Electroweak_Physics'; Problem='This topic studies whether UET-inspired electroweak relationships can reproduce selected decay, ratio, and coupling benchmarks.'; Variables='W/Z-related ratios, electroweak couplings, decay observables, and correction terms'; Assumptions='The topic uses effective comparison scripts against selected electroweak tables rather than a full gauge-theory derivation.'; Domain='Selected electroweak observables and decay-style benchmark datasets.'; Excluded='A complete replacement of the Standard Model electroweak sector or a full derivation of all gauge couplings.'; Parameter='Some coefficients and normalization choices remain calibration-sensitive.'; Baseline='LEP-style topic inputs, decay tables, and cited electroweak reference files.'; Metrics='relative error on selected electroweak ratios, decay observables, and benchmark residuals'; Limitation='The repository still needs a cleaner mapping from data files to the exact benchmark claim each script supports.'},
  [ordered]@{Name='0.7_Neutrino_Physics'; Problem='This topic studies whether UET-inspired neutrino structure can reproduce selected oscillation and weak-decay-related benchmarks.'; Variables='mixing angles, mass-squared differences, PMNS-style parameters, and decay observables'; Assumptions='The topic is currently an internal benchmark package around selected neutrino datasets and weak-process inputs.'; Domain='Selected oscillation and decay benchmarks represented in topic-local NuFit and related files.'; Excluded='A complete neutrino-sector theory across all matter effects, sterile sectors, or cosmological constraints.'; Parameter='Mixing and phase choices remain sensitive to the current benchmark framing.'; Baseline='NuFit working files, beta-decay inputs, and cited neutrino references.'; Metrics='angle residuals, mass-splitting residuals, and fit mismatch on selected neutrino observables'; Limitation='Proof-oriented wording must stay below the level of a full PMNS derivation until the case coverage is documented.'},
  [ordered]@{Name='0.8_Muon_g2_Anomaly'; Problem='This topic studies whether a UET-style correction term can numerically track the selected muon magnetic-moment discrepancy package in the repo.'; Variables='muon anomaly correction terms, magnetic-moment discrepancy values, and coupling-scale parameters'; Assumptions='The package should be treated as an internal anomaly-model benchmark built around selected experimental and baseline values.'; Domain='Selected muon g-2 reference values and related internal comparison scripts.'; Excluded='A definitive resolution of the Standard Model anomaly or exclusion of all competing explanations.'; Parameter='Correction terms and normalization choices remain calibration-sensitive.'; Baseline='Topic-local Fermilab and Standard-Model comparison files plus competitor scripts.'; Metrics='absolute or relative residual on the reported anomaly value and discrepancy-to-baseline comparison'; Limitation='The topic should remain an internal benchmark package until data provenance and numeric thresholds are frozen.'},
  [ordered]@{Name='0.9_Quantum_Nonlocality'; Problem='This topic studies whether UET-inspired correlation models can reproduce selected Bell-type and nonlocality benchmarks.'; Variables='correlation coefficients, Bell parameters, setting-dependent terms, and coupling corrections'; Assumptions='The current package behaves like a simulation and comparison environment for selected Bell-test style datasets.'; Domain='Selected Bell-inequality and nonlocality benchmarks represented in topic-local files.'; Excluded='A definitive foundational resolution of quantum mechanics or all loophole-free nonlocality questions.'; Parameter='Calibration and measurement-setting choices affect the interpretation of the current scripts.'; Baseline='Topic-local Bell datasets and cited experimental references.'; Metrics='Bell-parameter residuals, violation consistency checks, and script-reported fit diagnostics'; Limitation='Local repository copies exist, but they are not yet packaged as a standards-grade evidence contract.'},
  [ordered]@{Name='0.11_Phase_Transitions'; Problem='This topic studies whether UET-style transition rules can reproduce selected critical-point and order-parameter benchmarks.'; Variables='critical temperature, order parameter, critical exponents, and transition-scale quantities'; Assumptions='The topic is currently a phenomenological comparison package tied to selected critical-point datasets.'; Domain='Selected fluids and materials transition benchmarks represented in topic-local files.'; Excluded='A general renormalization-group derivation for all transition classes.'; Parameter='Critical exponents and fit settings remain dependent on the chosen benchmark subset.'; Baseline='NIST critical-point inputs and topic-local competitor or test scripts.'; Metrics='critical-point residuals, exponent mismatch, and script-reported transition diagnostics'; Limitation='The topic still needs a clearer split between exploratory test files and the single canonical verification workflow.'},
  [ordered]@{Name='0.12_Vacuum_Energy_Casimir'; Problem='This topic studies whether UET-style vacuum-energy and Casimir models can reproduce selected force-versus-separation benchmarks.'; Variables='plate separation, force, vacuum-energy density, geometry terms, and calibration constants'; Assumptions='The current scripts implement effective comparison against selected Casimir datasets and related material cases.'; Domain='Selected Casimir-style experimental benchmarks and topic-local calibration files.'; Excluded='A full solution to the cosmological-constant problem or a universal vacuum-energy derivation.'; Parameter='Geometry and calibration choices remain important in the current scripts.'; Baseline='Topic-local Casimir datasets, calibration files, and cited literature references.'; Metrics='force residuals as a function of separation and mismatch against selected reference curves'; Limitation='This topic should not use broad vacuum-resolution language until the benchmark and limitation boundaries are made explicit.'},
  [ordered]@{Name='0.13_Thermodynamic_Bridge'; Problem='This topic studies whether UET can connect entropy, information cost, and dissipation benchmarks under one bridge model.'; Variables='entropy, dissipated work, information cost, relaxation terms, and bridge coefficients'; Assumptions='The topic currently uses selected dissipation and information-thermodynamics benchmarks rather than a universal derivation.'; Domain='Selected Landauer-style and nonequilibrium thermodynamics comparisons represented in topic-local files.'; Excluded='A universal proof across all thermodynamic regimes or all coarse-graining choices.'; Parameter='Reported behavior depends on coarse-graining choices and selected bridge coefficients.'; Baseline='Berut-style, Cattaneo-style, and topic-local thermodynamic data files.'; Metrics='relative error on dissipation or entropy-linked observables and consistency of bridge trends'; Limitation='The data package still contains manual signals, so the topic cannot yet claim fully standardized data provenance.'},
  [ordered]@{Name='0.14_Complex_Systems'; Problem='This topic studies whether UET-style scaling and complexity rules can organize selected complex-systems benchmarks across domains.'; Variables='scaling exponents, network-style complexity measures, dynamical features, and coupling terms'; Assumptions='The topic uses heterogeneous local case studies rather than one uniform benchmark family.'; Domain='Selected biology, brain, plasma, or econophysics-style files stored in the topic workspace.'; Excluded='A universal causal law that rigorously covers all complex systems.'; Parameter='Normalization choices and dataset stitching strongly affect current cross-domain interpretations.'; Baseline='Topic-local plasma, biology, and brain-style working files plus cited references.'; Metrics='scaling-fit residuals, classification consistency, or internal trend diagnostics reported by scripts'; Limitation='The title and narrative are broader than the current evidence package, which remains heterogeneous and under-normalized.'},
  [ordered]@{Name='0.15_Cluster_Dynamics'; Problem='This topic studies whether UET-inspired cluster-dynamics models can reproduce selected galaxy-cluster observables and offsets.'; Variables='cluster mass, virial quantities, spatial offsets, and cluster-formation terms'; Assumptions='The topic is currently an effective astrophysical benchmark package around selected cluster observations.'; Domain='Selected cluster datasets such as Bullet Cluster and Chandra-derived working files.'; Excluded='A universal replacement for dark-matter modeling across all cluster physics.'; Parameter='Cluster selection, nuisance terms, and projection choices matter in the current comparisons.'; Baseline='Bullet Cluster coordinates, Chandra working files, and cited cluster references.'; Metrics='mass residuals, offset mismatch, and script-reported cluster-fit diagnostics'; Limitation='The topic has visible source data, but the verification contract still needs to be narrowed to one canonical benchmark path.'},
  [ordered]@{Name='0.16_Heavy_Nuclei'; Problem='This topic studies whether UET-style heavy-nuclei and fission models can reproduce selected high-mass nuclear benchmarks.'; Variables='binding energy, fission observables, stability-valley terms, and heavy-nuclei correction parameters'; Assumptions='The topic uses selected heavy-nuclei and fission benchmarks rather than a universal nuclear-force derivation.'; Domain='Heavy nuclei, fission, and related mass-table comparisons represented in topic-local files.'; Excluded='A complete first-principles theory for all nuclear stability and decay channels.'; Parameter='Fit sensitivity remains important for high-mass tails and stability-valley behavior.'; Baseline='AME2020 heavy-nuclei files and topic-local fission comparison scripts.'; Metrics='binding-energy residuals, fission benchmark mismatch, and stability-trend diagnostics'; Limitation='Methods and limitations are currently implicit in code and analysis notes rather than exposed as a standardized root package.'},
  [ordered]@{Name='0.17_Mass_Generation'; Problem='This topic studies whether UET-inspired information-drag ideas can reproduce selected particle-mass hierarchy benchmarks.'; Variables='particle masses, coupling-strength terms, hierarchy ratios, and Koide-style quantities'; Assumptions='The current package is an internal benchmark environment around selected lepton and Higgs-related files.'; Domain='Selected lepton-mass and coupling comparisons represented in topic-local PDG-style files.'; Excluded='A complete derivation of all Standard Model masses or a full replacement of the Higgs mechanism.'; Parameter='Hierarchy fits and ratio claims remain sensitive to the chosen benchmark framing.'; Baseline='PDG-derived topic files and topic-local verification scripts.'; Metrics='mass residuals, ratio mismatch, and script-reported hierarchy diagnostics'; Limitation='Strong claim language must remain downgraded until proof boundary and verification scope are documented explicitly.'},
  [ordered]@{Name='0.18_Mathnicry'; Problem='This topic studies whether UET-style discrete or information-manifold ideas support selected mathematical proof attempts and symbolic experiments.'; Variables='theorem-target quantities, stability measures, spectral variables, and algorithmic-scaling diagnostics'; Assumptions='The current topic is a proof-attempt workspace built from heuristics, symbolic reasoning, and bounded numerical experiments.'; Domain='Selected Riemann-style, P-vs-NP-style, Collatz-style, and related mathematical experiments in the repository.'; Excluded='Peer-reviewed theorem-level proofs of Millennium Problems or universal proof closure across all claimed cases.'; Parameter='Discretization choices, search bounds, and heuristic construction matter in the current scripts.'; Baseline='Classical theorem statements, topic-local proof scripts, and internal diagnostic outputs.'; Metrics='consistency checks, bounded-domain counterexample searches, and script-reported scaling or stability diagnostics'; Limitation='Presence of proof scripts does not by itself establish theorem-level correctness, so proof scope must stay explicit.'},
  [ordered]@{Name='0.19_Gravity_GR'; Problem='This topic studies whether UET-inspired gravity models can reproduce selected general-relativity and gravity-constant benchmarks.'; Variables='gravitational coupling, metric-like potentials, fluid-gravity terms, and short-range deviation parameters'; Assumptions='The topic currently uses effective comparison scripts against selected gravity datasets and references.'; Domain='Selected GR-style, G-constant, and short-range gravity benchmarks represented in topic-local files.'; Excluded='A complete replacement of general relativity across all observational regimes.'; Parameter='Boundary conditions and fit choices affect the current residuals and should be stated explicitly.'; Baseline='CODATA-style gravity inputs and topic-local short-range comparison files.'; Metrics='relative error on gravity benchmarks and residual mismatch on selected comparison curves'; Limitation='The topic needs clearer unit, regime, and boundary-condition framing before stronger physical claims are justified.'},
  [ordered]@{Name='0.20_Atomic_Physics'; Problem='This topic studies whether UET-style atomic models can reproduce selected spectral and multi-electron atomic benchmarks.'; Variables='energy levels, spectral-line positions, orbital-scale terms, and correction parameters'; Assumptions='The current package is an internal atomic benchmark environment for selected hydrogen, helium, and related data.'; Domain='Selected atomic spectra and multi-electron comparisons represented in topic-local NIST-style files.'; Excluded='A full QED derivation or universal many-body closure for all atoms.'; Parameter='Approximation choices beyond simple atoms remain important in the current scripts.'; Baseline='NIST spectral-line files and topic-local research scripts.'; Metrics='wavelength or energy residuals and mismatch against selected spectral baselines'; Limitation='The topic should stay framed as an internal atomic benchmark until verification thresholds and limitations are frozen.'},
  [ordered]@{Name='0.22_Biophysics_Origin_of_Life'; Problem='This topic studies whether UET-inspired biophysical complexity models can organize selected biological or neural proxy datasets.'; Variables='complexity proxies, biomarker-like features, neural-dynamics measures, and coupling terms'; Assumptions='The current data package is heterogeneous and appears to use biological and neural proxies as exploratory stand-ins.'; Domain='Exploratory biophysical-complexity benchmarks represented in topic-local evidence assets and downloaded files.'; Excluded='A full origin-of-life mechanism or a complete validated biochemical theory.'; Parameter='Proxy choice and preprocessing strongly affect interpretation in the current package.'; Baseline='Topic-local evidence assets, downloaded files, and cited biological references.'; Metrics='complexity-score consistency, classification diagnostics, or residual mismatch on selected proxy benchmarks'; Limitation='The topic title currently outruns the checked-in data package, which is still proxy-heavy and under-normalized.'},
  [ordered]@{Name='0.23_Unity_Scale_Link'; Problem='This topic studies whether UET can connect measurements across scales through a common coupling or scale-link structure.'; Variables='cross-scale coupling terms, H0-like quantities, high-redshift observables, and scale-link diagnostics'; Assumptions='The topic currently stitches heterogeneous datasets into exploratory cross-domain scaling tests.'; Domain='Selected cosmology, high-redshift, and cross-domain benchmark files stored in the topic workspace.'; Excluded='A rigorous proof of one universal scale law across all domains.'; Parameter='Normalization and dataset-stitching choices are important and must stay visible.'; Baseline='Topic-local H0-tension, high-redshift, and unified-data working files.'; Metrics='cross-dataset residuals, consistency scores, and scaling-trend diagnostics'; Limitation='The evidence package remains exploratory because local materials are not yet packaged into a single auditable provenance chain.'},
  [ordered]@{Name='0.24_Artificial_Intelligence'; Problem='This topic studies whether UET-inspired scaling and efficiency ideas can explain selected AI benchmark behavior.'; Variables='scaling-law exponents, efficiency terms, latent-space quantities, and model-size descriptors'; Assumptions='The topic is currently an internal AI benchmark package tied to selected scaling-law and model metadata files.'; Domain='Selected foundation-model scaling and AI efficiency comparisons represented in topic-local data files.'; Excluded='A general proof about intelligence, reasoning, or universal AI dynamics.'; Parameter='Benchmark choice, preprocessing, and proxy metrics remain important to interpretation.'; Baseline='GPT-style scaling-law files and topic-local AI model metadata.'; Metrics='scaling residuals, efficiency comparisons, and script-reported benchmark diagnostics'; Limitation='Even with conservative README language, the topic still lacks a standardized verification contract and explicit limitations package.'},
  [ordered]@{Name='0.25_Strategy_Power_Economics'; Problem='This topic studies whether UET-inspired strategic and economic dynamics can reproduce selected macro and power-related benchmarks.'; Variables='macro indicators, network or power terms, financial time-series quantities, and stability measures'; Assumptions='The current package is an internal socio-economic modeling workspace built on selected topic-local datasets.'; Domain='Selected global-economy, financial, and strategy-oriented time series represented in the topic workspace.'; Excluded='A causal proof of geopolitical or economic laws across all regimes.'; Parameter='Regime changes, exogenous shocks, and preprocessing choices strongly affect the present comparisons.'; Baseline='Global_Economy_2024, Bitcoin Yahoo data, and topic-local research scripts.'; Metrics='fit residuals, trend mismatch, and script-reported stability diagnostics'; Limitation='The topic should stay framed as an exploratory benchmark package because socio-economic causality is not closed by internal scripts alone.'},
  [ordered]@{Name='0.26_Cosmic_Dynamic_Frame'; Problem='This topic studies whether UET-inspired dynamic-cosmos framing can reproduce selected cosmic-flow and anomaly benchmarks.'; Variables='cosmic-flow quantities, dynamic-viscosity terms, anomaly corrections, and background-frame parameters'; Assumptions='The current scripts behave like effective cosmology comparisons on selected flow and anomaly datasets.'; Domain='Selected cosmic-flow, Pioneer-anomaly-style, and related dynamic-cosmos comparisons stored in the topic workspace.'; Excluded='A full replacement of consensus cosmology or a universal derivation of all large-scale structure dynamics.'; Parameter='Background selection and fitted anomaly terms remain sensitive in the current scripts.'; Baseline='Cosmicflows-3 subset, Pioneer anomaly files, and topic-local research scripts.'; Metrics='residuals on flow or anomaly observables and internal comparison diagnostics'; Limitation='Manual data signals are still present, so stronger physical claims must wait for a cleaner manifest-backed pipeline.'}
)

$specByName = @{}
foreach ($spec in $specs) { $specByName[$spec.Name] = $spec }
$readinessJson = Get-Content 'docs/meta/topic_readiness.json' -Raw | ConvertFrom-Json
$readinessByName = @{}
foreach ($entry in $readinessJson.topics) { $readinessByName[$entry.name] = $entry }

function RelPath($root, $item) {
  if (-not $item) { return $null }
  return $item.FullName.Substring($root.FullName.Length + 1).Replace('\','/')
}

function Get-FirstFiles($path, $pattern='*', $count=3) {
  if (-not (Test-Path $path)) { return @() }
  return @(Get-ChildItem $path -File -Filter $pattern -ErrorAction SilentlyContinue | Sort-Object Name | Select-Object -First $count)
}

function Pick-PrimaryCommand($topic) {
  $researchDir = Join-Path $topic.FullName 'Code/03_Research'
  $engineDir = Join-Path $topic.FullName 'Code/01_Engine'
  $verify = @(Get-ChildItem $researchDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(Verify|Research|Experiment|test_)' } | Sort-Object Name)
  if ($verify.Count -gt 0) { return RelPath $topic $verify[0] }
  $engine = Get-FirstFiles $engineDir '*' 1
  if ($engine.Count -gt 0) { return RelPath $topic $engine[0] }
  return $null
}

function Infer-Source($name) {
  switch -Regex ($name) {
    'AME2020' { return 'AME2020 working copy' }
    'PDG' { return 'PDG working copy' }
    'NIST' { return 'NIST working copy' }
    'NuFit' { return 'NuFit working copy' }
    'Fermilab|Muon' { return 'Muon g-2 / Fermilab working copy' }
    'Cosmicflows|Pioneer' { return 'Cosmicflows or anomaly working copy' }
    'Chandra|Bullet' { return 'Cluster-observation working copy' }
    'BlackHole|EHT' { return 'Black-hole observation working copy' }
    'SPARC|little_things' { return 'Galaxy-rotation working copy' }
    'Supercon|superconduct' { return 'Supercon or superconductivity working copy' }
    'casimir' { return 'Casimir reference working copy' }
    'berut|cattaneo|entropy' { return 'Information-thermodynamics working copy' }
    'bell|quantum' { return 'Quantum-foundations working copy' }
    'economy|Bitcoin|GDP' { return 'Economic working copy' }
    default { return 'Topic-local working copy or generated benchmark input' }
  }
}

function ProvenanceText($status) {
  switch ($status) {
    'no data path' { return 'No canonical topic-local dataset is currently defined.' }
    'embedded local only' { return 'Local repository copy; upstream source normalization still needs work.' }
    'manual or placeholder' { return 'Manual, placeholder, or partially scripted data handling is still present.' }
    'real source referenced' { return 'Real source is referenced, but manifest normalization is still in progress.' }
    'manifested real dataset' { return 'Manifest-backed repository copy.' }
    default { return 'Provenance normalization status not yet frozen.' }
  }
}

$topics = Get-ChildItem 'docs/topics' -Directory | Where-Object { $_.Name -match '^0\.(?:[0-9]|1[0-9]|2[0-6])_' } | Sort-Object Name
foreach ($topic in $topics) {
  if (@('0.1_Galaxy_Rotation_Problem','0.3_Cosmology_Hubble_Tension','0.10_Fluid_Dynamics_Chaos','0.21_Yang_Mills_Mass_Gap') -contains $topic.Name) { continue }
  $spec = $specByName[$topic.Name]
  if (-not $spec) { continue }
  $meta = $readinessByName[$topic.Name]

  $engineFiles = Get-FirstFiles (Join-Path $topic.FullName 'Code/01_Engine') '*' 3
  $proofFiles = Get-FirstFiles (Join-Path $topic.FullName 'Code/02_Proof') '*' 3
  $researchFiles = Get-FirstFiles (Join-Path $topic.FullName 'Code/03_Research') '*' 3
  $dataFiles = @(Get-ChildItem (Join-Path $topic.FullName 'Data') -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -notin @('.png','.jpg','.jpeg','.svg','.bib') } |
    Sort-Object FullName | Select-Object -First 4)
  if ($dataFiles.Count -eq 0) {
    $dataFiles = @(Get-ChildItem (Join-Path $topic.FullName 'Data') -File -Recurse -ErrorAction SilentlyContinue | Sort-Object FullName | Select-Object -First 4)
  }
  $dataFiles = @(
    $dataFiles |
    Group-Object { RelPath $topic $_ } |
    ForEach-Object { $_.Group[0] }
  )

  $engineLines = if ($engineFiles.Count) { ($engineFiles | ForEach-Object { '- `' + (RelPath $topic $_) + '`' }) -join "`n" } else { '- No engine file was auto-detected in `Code/01_Engine/`.' }
  $proofLines = if ($proofFiles.Count) { ($proofFiles | ForEach-Object { '- `' + (RelPath $topic $_) + '`' }) -join "`n" } else { '- No proof file was auto-detected in `Code/02_Proof/`.' }
  $researchLines = if ($researchFiles.Count) { ($researchFiles | ForEach-Object { '- `' + (RelPath $topic $_) + '`' }) -join "`n" } else { '- No research file was auto-detected in `Code/03_Research/`.' }
  $commandPath = Pick-PrimaryCommand $topic
  $commandLine = if ($commandPath) { '`python docs/topics/' + $topic.Name + '/' + $commandPath + '`' } else { 'No canonical command has been locked yet.' }
  $artifactSlug = ($topic.Name -replace '[^A-Za-z0-9]+','_').ToLowerInvariant().Trim('_')
  $artifactPath = 'Result/artifacts/' + $artifactSlug + '_verification.json'

  $dataRows = @()
  foreach ($df in $dataFiles) {
    $rel = RelPath $topic $df
    $src = Infer-Source $df.Name
    $prov = ProvenanceText $meta.data_reality_status
    $dataRows += '| ' + $df.Name + ' | `' + $rel + '` | ' + $src + ' | ' + $prov + ' |'
  }
  if ($dataRows.Count -eq 0) {
    $dataRows += '| none currently locked | `n/a` | No canonical topic-local dataset currently defined | ' + (ProvenanceText $meta.data_reality_status) + ' |'
  }

  $inputLines = if ($dataFiles.Count) { ($dataFiles | ForEach-Object { '  - `' + (RelPath $topic $_) + '`' }) -join "`n" } else { '  - No canonical topic-local dataset is currently locked.' }

  $method = @"
# Method

## Problem target

$($spec.Problem)

## Core components

### Engine components
$engineLines

### Proof-oriented components
$proofLines

### Research and comparison components
$researchLines

## Variable framing

- Primary modeled quantities: $($spec.Variables)

## Assumptions

- $($spec.Assumptions)

## Domain of validity

- $($spec.Domain)

## Excluded cases

- $($spec.Excluded)

## Parameter sensitivity note

- $($spec.Parameter)
"@

  $dataManifest = @"
# Data Manifest

Current data reality status: "$($meta.data_reality_status)"

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
$($dataRows -join "`n")

Repository note:

- This manifest was created during the repo standards pass and should be tightened further in a later provenance-normalization wave.
- Until upstream URLs, DOIs, preprocessing notes, and hashes are frozen, treat the dataset package as an internal working copy rather than an archival release.
"@

  $verification = @"
# Verification Spec

- Primary command:
  - $commandLine
- Inputs:
$inputLines
- Baseline:
  - $($spec.Baseline)
- Reported metrics:
  - $($spec.Metrics)
- Fixed threshold:
  - Working threshold for this standards pass: the primary script must run without error, use the stated input package, and write a summary artifact under Result/artifacts/. A stronger numeric acceptance threshold must be frozen in a later BASELINE_COMPARISON.md pass.
- Artifact target:
  - $artifactPath
- Interpretation:
  - Treat output as an internal benchmark artifact only. Do not upgrade claim language to 'solved', 'verified', or 'exact' until a topic-specific baseline-comparison pass is complete.
"@

  $baselineComparison = @"
# Baseline Comparison

## Baseline target

- $($spec.Baseline)

## Current comparator package

- Comparator or reference scripts should be taken from topic-local Code/04_Competitor/ when present.
- If no dedicated competitor script exists, the baseline is the cited source dataset or reference model listed in DATA_MANIFEST.md.

## Comparison metrics

- $($spec.Metrics)

## Acceptance boundary

- This file does not certify a final pass/fail result.
- Until the benchmark is rerun with a saved artifact, comparison language must remain internal benchmark comparison.
- A future hardening pass must record the exact numeric threshold, generated artifact, timestamp, environment, and dataset hash.

## Claim boundary

- This baseline comparison can support only conservative wording such as matched selected benchmarks or internal comparison workflow.
- It does not support wording such as solved, verified, exact, unified, or production grade.
"@

  $limitations = @"
# Limitations

- The root baseline comparison is present, but numeric acceptance boundaries are still provisional until a saved artifact is generated and reviewed.
- Current data posture is "$($meta.data_reality_status)", which is below a fully normalized archival dataset package.
- $($spec.Limitation)
- Internal script execution does not by itself establish external replication, theorem-level proof, or broad physical closure.
"@

  Set-Content -Path (Join-Path $topic.FullName 'METHOD.md') -Value $method -Encoding UTF8
  Set-Content -Path (Join-Path $topic.FullName 'DATA_MANIFEST.md') -Value $dataManifest -Encoding UTF8
  Set-Content -Path (Join-Path $topic.FullName 'VERIFICATION_SPEC.md') -Value $verification -Encoding UTF8
  Set-Content -Path (Join-Path $topic.FullName 'BASELINE_COMPARISON.md') -Value $baselineComparison -Encoding UTF8
  Set-Content -Path (Join-Path $topic.FullName 'LIMITATIONS.md') -Value $limitations -Encoding UTF8
}

Write-Output 'Generated standards package docs for missing core topics.'
