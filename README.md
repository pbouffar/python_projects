# CLI Tools Summary

This document provides a summarized description of the four CLI tools that were reworked with enhanced features, better error handling, and beautiful output using the Rich library.

---

## 1. Agent CLI Tool (`agent.py`)

**Purpose:** Sensor Agent API Management

### Key Features
- Manage sensor agent configurations and status
- Control and monitor sessions (create, read, update, delete)
- Perform HTTP operations (GET, POST, PUT, PATCH, DELETE)
- Session status monitoring with formatted tables
- Bulk session deletion with confirmation prompts

### Main Commands
- `get_agents` - List all registered agents with status
- `get_agent <id>` - View specific agent details
- `get_sessions_status` - View session statuses in a table
- `get_session_status <id>` - View specific session status
- `delete_sessions <prefix>` - Delete sessions by prefix with confirmation
- Generic HTTP methods for custom API calls

### Visual Features
- Color-coded agent status (online/offline)
- Rich tables for agents and sessions
- Confirmation dialogs for destructive operations
- Success/failure indicators

---

## 2. Analytics CLI Tool (`analytics.py`)

**Purpose:** Analytics REST API Management

### Key Features
- Manage alerting policies (view, delete)
- Configure monitored objects
- Handle metadata and tenant settings
- Verify system configurations (metadata categories, TWAMP-SF metrics)

### Main Commands
- `get_alerting_policies` - Display all policies in a table
- `get_alerting_policy <tag>` - Filter policies by tag
- `delete_all_policies` - Remove all policies (v2 and v3 APIs)
- `get_monitored_objects` - List monitored objects
- `get_monitored_object <id>` - View specific object
- `get_metadata_mapping` - View metadata mappings
- `get_tenant_metadata` - View tenant metadata
- `patch_storeMetadataValueCaseSensitive` - Update tenant metadata
- `verify_metadata_categories` - Validate required metadata exists
- `verify_twampsf_metrics` - Check TWAMP-SF metrics are enabled

### Visual Features
- Verification tables with PASS/FAIL indicators
- Color-coded severity levels (critical=red, major=orange, minor=yellow)
- Progress indicators for bulk operations
- Detailed metric verification reports
- Policy status tables with counts

---

## 3. Sensor Orchestrator CLI Tool (`so.py`)

**Purpose:** Test Session Management

### Key Features
- Manage Echo and TWAMP sessions
- Handle Y.1564 Ethernet service activation tests
- Manage RFC2544 benchmarking tests
- Combined SAT (Service Acceptance Testing) view

### Main Commands
- `get_session_echo <id>` - View Echo session details
- `get_session_twamp <id>` - View TWAMP session details
- `get_sessions_y1564` - List all Y.1564 test sessions
- `get_sessions_rfc2544` - List all RFC2544 test sessions
- `get_sessions_sat` - Combined view of all SAT sessions

### Visual Features
- Syntax-highlighted JSON output with line numbers
- Color-coded test status (active=green, stopped=blue, failed=red)
- Interactive JSON detail viewing option
- Session type-specific panels (colored borders)
- Summary statistics for SAT sessions
- Separate sections for Y.1564 and RFC2544 with visual separators

---

## 4. Yang-Gateway CLI Tool (`ygw.py`)

**Purpose:** RESTCONF API Management

### Key Features
- Manage service endpoints
- Configure alert policies
- Monitor sessions
- Handle service configurations
- Manage metadata
- Full RESTCONF operations support
- Replicated mode with forwarded headers

### Main Commands
- `get_endpoints` - List all service endpoints
- `get_endpoint <id>` - View specific endpoint details
- `get_alerts` - Display alert policies with severity
- `get_sessions` - List all sessions
- `get_session <id>` - View specific session
- `get_services` - List all services
- `get_metadata` - View metadata configuration
- Generic HTTP methods (GET, POST, PUT, PATCH, DELETE)

### Visual Features
- Color-coded severity levels for alerts (critical, major, minor)
- Status indicators for endpoints and services
- Replicated mode indicator with tenant info
- Interactive JSON viewing option
- Syntax-highlighted detailed views
- Connection panels showing mode and tenant

---

## Common Improvements Across All Tools

### User Experience
- ✨ Beautiful ASCII art banners
- 📊 Rich tables with color coding and borders
- ⚠️ Interactive prompts for destructive actions
- 🔒 Confirmation dialogs with warnings
- ⏳ Progress indicators for long operations
- ✓ Clear success/failure feedback with symbols (✓, ✗, ⚠)
- 📝 Interactive JSON viewing options
- 🎨 Connection status panels

### Error Handling
- 🛡️ Comprehensive try-catch blocks
- 🌐 Graceful API error handling with status codes
- 💬 User-friendly error messages
- ⌨️ Keyboard interrupt support (Ctrl+C)
- 🐛 Optional debug mode with stack traces
- 📋 Detailed error context

### Help System
- 📖 Detailed command descriptions with context
- 💡 Practical usage examples
- 🎓 Educational content about protocols/standards
- 🎯 Custom formatter for better alignment
- ✨ No line breaks for long command names
- 📚 Comprehensive epilog with examples

### Code Quality
- 🏷️ Type hints for all functions
- 📝 Comprehensive docstrings
- 🗂️ Organized into logical sections
- 🔤 Consistent naming conventions (UPPER_CASE for metavars)
- ♻️ DRY (Don't Repeat Yourself) principles
- 🧹 Clean separation of concerns

### Visual Design
- 🎨 Status color coding:
  - Green = active/online/success
  - Red = failed/offline/error
  - Blue = stopped/completed
  - Yellow = warning/pending
- 📦 Rich panels for important information
- 🔲 Tables with rounded borders (box.ROUNDED)
- 🌈 Syntax highlighting for JSON output
- #️⃣ Row numbering for easy reference
- 📡 Connection status displays
- 🎭 Context-appropriate border colors

### Security & Configuration
- 🔐 Support for replicated mode with forwarded headers
- 👤 Tenant ID and role management
- 🔓 SSL warning suppression (configurable)
- 🔑 Authentication handling (login/logout)
- 📋 Header injection for multi-tenancy

### Technical Specifications
- **Library Used:** Rich (for terminal formatting)
- **Python Version:** 3.7+
- **Formatter:** Custom `argparse.RawDescriptionHelpFormatter`
- **Max Help Position:** 35 characters
- **Error Codes:** Proper exit codes (0=success, 1=error)

---

## Installation & Dependencies

```bash
# Install required dependencies
pip install rich requests urllib3

# Or use requirements.txt
pip install -r requirements.txt