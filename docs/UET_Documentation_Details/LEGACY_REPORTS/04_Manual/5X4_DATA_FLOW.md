# 5x4 Grid Data Flow Architecture 🧬

This diagram illustrates how a Simulation Script interacts with the Core System to automatically route results to the correct 5x4 Grid Location.

## The Logic Flow

```mermaid
graph TD
    %% Actors and Inputs
    Script["User Script<br>(e.g. Research_Galaxy.py)"]
    Config["Params<br>(Mass, Radius)"]

    %% The Core Solver
    subgraph "Core System (Glass Box)"
        Solver["UETBaseSolver"]
        PathMan["UETPathManager"]
        Logger["UETMetricLogger"]
    end

    %% The File System (Target)
    subgraph "File System (5x4 Grid)"
        TopicDir["topics/0.1_Galaxy.../"]
        ResRoot["Result/"]
        
        subgraph " Pillars (The Decision) "
            P1["01_Engine/"]
            P2["02_Proof/"]
            P3["03_Research/"]
        end
        
        RunFolder["[Timestamp]_[RunName]/"]
        Files["summary.json<br>timeseries.csv<br>plot.png"]
    end

    %% Connections
    Script -- "1. Init(pillar='03_Research')" --> Solver
    Config -- "2. Pass Params" --> Solver
    
    Solver -- "3. Request Path(topic, pillar)" --> PathMan
    
    PathMan -- "4. Find Topic Folder" --> TopicDir
    PathMan -- "5. Select Pillar" --> P3
    PathMan -- "6. Create RunID" --> RunFolder
    
    Solver -- "7. Init Logger" --> Logger
    Logger -- "8. Write Data" --> Files

    %% Layout
    TopicDir --> ResRoot
    ResRoot --> P1
    ResRoot --> P2
    ResRoot --> P3
    P3 --> RunFolder
    RunFolder --> Files
```

## How the Decision is Made 🧠

1.  **Who Decides?** The **Script** decides where it lives.
    *   If you are writing a script in `Code/03_Research`, you initialize the engine with `pillar="03_Research"`.
    *   `engine = UETGalaxyEngine(..., pillar="03_Research")`

2.  **How is the Folder Created?**
    *   **Level 1 (Topic):** [UETPathManager](file:///c:/Users/santa/Desktop/lad/Lab_uet_harness_v0.9.0/docs/scripts/core/runners/uet_glass_box.py#27-95) finds `topics/0.1_Galaxy...` automatically.
    *   **Level 2 (Result Root):** Enters `/Result`.
    *   **Level 3 (Pillar):** Uses the `pillar` argument (e.g., `03_Research`). **This is where the split happens.**
    *   **Level 4 (RunID):** Creates a unique folder `[Timestamp]_[ExperimentName]`.

## Example Result Path
`topics/0.1_Galaxy_Rotation_Problem/Result/03_Research/1768958913_MyGalaxyTest/`

This ensures that Engine tests stay in `01_Engine`, and Research outputs stay in `03_Research`.


