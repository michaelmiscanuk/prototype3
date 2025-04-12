# 2. Data Processing Sequence

```mermaid
sequenceDiagram
    %% Participants in order of interaction
    actor User as User
    participant SafeLauncher as Safe Launcher
    participant EntryPoint as Application Entry
    participant Observability as Observability Layer
    participant Flow as Analysis Flow
    participant AgentSystem as Agent System
    participant Agent as Data Query Agent
    participant QueryTool as Query Tool
    participant DataSource as Data Store
    participant LLM as Reasoning Engine
    
    %% Application startup with proper sequence
    User->>SafeLauncher: Launch application
    SafeLauncher->>EntryPoint: Execute entry point
    EntryPoint->>Observability: Initialize monitoring
    Observability-->>EntryPoint: Return tracer provider
    EntryPoint->>Observability: Open execution span
    
    %% Flow initialization
    EntryPoint->>Flow: Initialize flow
    activate Flow
    
    %% Step 1: Input processing
    Flow->>Flow: Process input data
    activate Flow
    Note right of Flow: Load schema from metadata
    Note right of Flow: Set analysis query
    deactivate Flow
    
    %% Step 2: Analysis execution
    Flow->>AgentSystem: Initialize agent system
    activate AgentSystem
    
    %% Agent setup and task definition
    AgentSystem->>Agent: Create data query agent
    activate Agent
    AgentSystem->>Agent: Assign analysis task
    Note right of Agent: Task includes query and schema
    
    %% Tool usage
    Agent->>LLM: Request query formulation
    LLM-->>Agent: Return generated query
    Agent->>QueryTool: Execute data query
    activate QueryTool
    QueryTool->>DataSource: Access data
    DataSource-->>QueryTool: Return raw data
    QueryTool->>QueryTool: Execute analysis operation
    QueryTool-->>Agent: Return query result
    deactivate QueryTool
    
    %% Result processing
    Agent->>LLM: Request result formatting
    LLM-->>Agent: Return formatted analysis
    Agent-->>AgentSystem: Return final analysis
    deactivate Agent
    
    AgentSystem-->>Flow: Return result
    deactivate AgentSystem
    
    %% Step 3: Result persistence
    Flow->>Flow: Save analysis result
    activate Flow
    Note right of Flow: Write to output file
    deactivate Flow
    
    %% Complete the flow
    Flow-->>EntryPoint: Complete analysis
    deactivate Flow
    EntryPoint-->>User: Return completion status
    
    %% Tracing completion
    Observability->>Observability: Close monitoring span
```

## Sequence Description

This sequence diagram illustrates the precise order of operations and interactions between components:

1. **Execution Initiation**
   - User launches the application via the `Safe Launcher`.
   - The application entry point initializes the observability layer.
   - A monitoring span is established for the execution.

2. **Flow Setup**
   - The analysis flow is initialized.
   - Input processing occurs: schema loading and query setup.
   - The flow prepares the state with necessary data.

3. **Agent System Activation**
   - An agent system is initialized with the analysis context.
   - A data query agent is created with domain expertise.
   - A specific task is assigned to the agent with instructions.

4. **Analysis Execution**
   - The agent uses the reasoning engine to formulate a query.
   - The query is executed via the query tool.
   - The tool accesses the data store and runs the analysis operation.

5. **Result Processing**
   - Raw query results are formatted by the reasoning engine.
   - The formatted analysis is returned through the component chain.
   - The analysis result is persisted to storage.

6. **Execution Completion**
   - The flow execution completes.
   - The monitoring span is closed.
   - Completion status is returned to the user.

This sequence accurately reflects the actual execution order in the application code, showing how data and control flow between components.
