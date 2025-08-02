# AI Context Directory

This directory contains structured context information for AI assistants working on this project. It follows a general memory bank concept that can be used with any AI tool (Cursor, Claude, GitHub Copilot, etc.).

## 🧠 How to Use This Context

### For AI Tools
Different AI tools can consume this context in various ways:

#### Cursor
- Add this directory to your `.cursorrules` file:
  ```
  # Read AI context from ai-context/ directory
  Always read the ai-context/ directory first to understand project context.
  ```

#### Claude/ChatGPT
- Include relevant context files in your conversation by copying content from:
  - `project-brief.md` - Project overview
  - `active-context.md` - Current work focus

#### GitHub Copilot
- Reference context files in comments:
  ```python
  # See ai-context/system-patterns.md for architecture decisions
  ```

#### VS Code Extensions
- Use workspace settings to reference context:
  ```json
  {
    "ai.contextFiles": ["ai-context/**/*.md"]
  }
  ```

## 📁 Context Structure

### Core Files (Always Read These)
1. **`project-brief.md`** - Foundation document that defines the project
2. **`product-context.md`** - What the product does and why it exists
3. **`system-patterns.md`** - Architecture, patterns, and technical decisions
4. **`tech-context.md`** - Technologies, tools, and setup information
5. **`active-context.md`** - Current work focus and recent changes
6. **`progress.md`** - Current status, what works, what needs to be done

### Specialized Files
- **`api-patterns.md`** - API design patterns and conventions
- **`testing-strategy.md`** - Testing approaches and frameworks
- **`deployment.md`** - Deployment processes and infrastructure

## 🔄 Maintenance

### When to Update
- After implementing significant features
- When architecture changes
- Before starting new work phases
- When onboarding new team members or AI assistants

### Update Process
1. Review all core files for accuracy
2. Update `active-context.md` with current focus
3. Update `progress.md` with latest status
4. Add new specialized files as needed

## 🤖 AI Assistant Instructions

When working with this project:

1. **Always start by reading** `project-brief.md` and `active-context.md`
2. **Refer to** `system-patterns.md` for architecture decisions
3. **Check** `tech-context.md` for technology constraints
4. **Update** `active-context.md` after significant changes
5. **Maintain** context accuracy throughout the session

This context system ensures consistent understanding across different AI tools and sessions.