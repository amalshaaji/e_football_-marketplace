# Product Requirements Document (PRD)
# eFootball Account Marketplace

**Version:** 1.0
**Status:** Development Plan
**Architecture:** Modular Monolith
**Frontend:** React + Vite
**Backend:** FastAPI
**Database:** PostgreSQL

---

## 1. Product Overview

The eFootball Account Marketplace is a web platform for browsing, listing, buying, and managing eFootball game accounts.

The platform will provide:

- Account listings
- Search, filters, sorting, and pagination
- Buyer and seller accounts
- Seller listings
- Orders
- Payments
- Favorites
- Reviews
- Buyer/seller messaging
- Notifications
- Reports and moderation
- Admin management
- Security controls
- Scalable infrastructure

The first implementation will use a **modular monolith**. Business features will be isolated into modules while the application remains one deployable backend. The architecture should allow later horizontal scaling or selective service extraction if justified by actual requirements.

> Before launch, verify that account trading/transfers and related commercial activity comply with current eFootball/KONAMI terms, applicable laws, payment-provider requirements, and consumer-protection rules.

---

# 2. Product Goals

## Primary Goals

1. Provide a professional marketplace experience.
2. Make account discovery simple and fast.
3. Provide clear and structured listing information.
4. Separate buyer, seller, and administrator workflows.
5. Provide secure authentication and authorization.
6. Provide reliable order and payment workflows.
7. Provide moderation and reporting tools.
8. Maintain clean, maintainable, modular code.
9. Prepare the platform for increasing traffic.
10. Provide a foundation for future mobile apps and additional services.

---

# 3. User Roles

## Buyer

A buyer can:

- Register and log in.
- Browse listings.
- Search and filter listings.
- View account details.
- Save favorites.
- Place orders.
- Complete supported payment flows.
- View order history.
- Communicate with sellers where permitted.
- Review eligible completed transactions.
- Submit reports/support requests.

## Seller

A seller can:

- Create and manage a profile.
- Create listings.
- Upload listing images.
- Edit listings.
- Manage listing status.
- View orders.
- Complete the supported delivery/transfer workflow.
- View sales history.
- Communicate with buyers where permitted.
- Receive reviews.

## Administrator

An administrator can:

- Manage users.
- Moderate listings.
- Review reports.
- Inspect orders and payments.
- Moderate reviews.
- Manage platform settings.
- Perform controlled administrative actions.
- Review operational statistics.
- Access audit records.

---

# 4. Core Modules

The application is divided into these business modules:

```text
auth
users
accounts
listings
orders
payments
reviews
favorites
messages
notifications
reports
admin
```

Future modules can be added without restructuring the entire backend.

---

# 5. Technology Stack

## Frontend

- React
- Vite
- JavaScript / ES6+
- React Router
- ESLint

## Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy 2.x
- Alembic

## Database

- PostgreSQL

## Future Infrastructure

Introduce only when required by the relevant phase:

- Redis
- Background workers
- Object storage
- CDN
- Cloudflare
- Nginx
- Monitoring
- Error tracking
- CI/CD

---

# 6. High-Level Architecture

```text
Users
  |
  v
Cloudflare / CDN
  |
  v
Nginx / Reverse Proxy
  |
  +--------------------+
  |                    |
  v                    v
React + Vite         FastAPI
                        |
              +---------+---------+
              |                   |
              v                   v
         PostgreSQL             Redis
                                  |
                           Cache / Queue
                                  |
                                  v
                         Background Workers
```

Initial application architecture:

```text
React
  |
  v
FastAPI Router
  |
  v
Service
  |
  v
Repository
  |
  v
PostgreSQL
```

---

# 7. Repository Structure

```text
efootball-marketplace/
│
├── apps/
│   ├── web/
│   └── api/
│
├── packages/
│   ├── shared-types/
│   ├── shared-config/
│   └── shared-utils/
│
├── database/
│   └── seeds/
│
├── infrastructure/
│   ├── nginx/
│   ├── docker/
│   ├── cloudflare/
│   └── monitoring/
│
├── storage/
│
├── scripts/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── security/
│   └── deployment/
│
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── README.md
└── LICENSE
```

---

# 8. Frontend Architecture

```text
apps/web/src/
│
├── assets/
├── components/
│   ├── ui/
│   ├── layout/
│   └── common/
│
├── features/
│   ├── auth/
│   ├── accounts/
│   ├── listings/
│   ├── orders/
│   ├── payments/
│   ├── messages/
│   ├── reviews/
│   └── favorites/
│
├── pages/
│   ├── home/
│   ├── marketplace/
│   ├── listing/
│   ├── auth/
│   ├── buyer/
│   ├── seller/
│   └── admin/
│
├── hooks/
├── services/
├── routes/
├── store/
├── utils/
├── constants/
├── types/
├── config/
├── App.jsx
└── main.jsx
```

---

# 9. Backend Architecture

```text
apps/api/app/
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── permissions.py
│   ├── exceptions.py
│   └── logging.py
│
├── database/
│   ├── connection.py
│   ├── session.py
│   └── base.py
│
├── modules/
│   ├── auth/
│   ├── users/
│   ├── accounts/
│   ├── listings/
│   ├── orders/
│   ├── payments/
│   ├── reviews/
│   ├── favorites/
│   ├── messages/
│   ├── notifications/
│   ├── reports/
│   └── admin/
│
├── middleware/
└── tasks/
```

A mature feature module can contain:

```text
models.py
schemas.py
router.py
service.py
repository.py
dependencies.py
```

Only create files that are actually needed.

---

# 10. Core Data Model

Initial entities:

```text
users
user_profiles
accounts
account_images
listings
orders
payments
reviews
favorites
conversations
messages
notifications
reports
audit_logs
```

Relationships:

```text
User
 ├── Profile
 ├── Listings
 ├── Orders
 ├── Reviews
 ├── Favorites
 ├── Conversations
 ├── Notifications
 └── Reports

Listing
 ├── Account
 ├── Seller
 ├── Images
 └── Order

Order
 ├── Buyer
 ├── Seller
 ├── Listing
 └── Payment
```

The final schema must be designed and reviewed during Phase 3 before production implementation.

---

# 11. Functional Requirements

## 11.1 Authentication

The system should support:

- Registration
- Login
- Logout
- Password hashing
- Password reset
- Email verification
- Secure authentication
- Role-based authorization
- Session/token expiration

Roles:

```text
BUYER
SELLER
ADMIN
```

Backend authorization must never rely only on client-side role information.

---

## 11.2 User Profiles

Users should have:

- Username/display name
- Profile image
- Account status
- Registration date
- Seller information where applicable
- Reviews/ratings where applicable
- Basic account settings

Sensitive information must not be publicly exposed.

---

## 11.3 Accounts

An account record represents the game account being listed.

The system should support structured account information rather than storing all information as one text field.

Account data may include:

- Platform
- Game/account attributes
- Player/team information
- Progression information
- Screenshots
- Additional marketplace-approved attributes

The exact fields will be finalized during Phase 3.

---

## 11.4 Listings

A listing should support:

- Title
- Description
- Price
- Account
- Images
- Seller
- Listing status
- Creation date
- Updated date

Example lifecycle:

```text
DRAFT
  ↓
PENDING_REVIEW
  ↓
ACTIVE
  ├── RESERVED
  ├── SOLD
  ├── REJECTED
  └── ARCHIVED
```

---

## 11.5 Marketplace

The marketplace should support:

- Listing grid
- Listing cards
- Listing details
- Search
- Filters
- Sorting
- Pagination
- Responsive design
- Listing status
- Seller information
- Price
- Image gallery

Search should initially use PostgreSQL capabilities where practical. A dedicated search engine should only be introduced if actual scale and requirements justify it.

---

## 11.6 Favorites

Users can:

- Add listing to favorites
- Remove listing from favorites
- View saved listings
- Handle sold/unavailable listings appropriately

Database constraints should prevent duplicate favorites.

---

## 11.7 Orders

Orders should support:

- Order creation
- Buyer
- Seller
- Listing
- Price
- Order status
- Payment reference
- Timestamps
- Order history
- Cancellation where supported
- Dispute/report integration

Example lifecycle:

```text
PENDING
  ↓
PAYMENT_PENDING
  ↓
PAID
  ↓
PROCESSING
  ↓
COMPLETED
```

Additional states such as cancellation, refund, or dispute should be explicitly modeled.

---

## 11.8 Payments

Payment architecture should support:

- Payment initiation
- Provider reference
- Payment status
- Verification
- Webhooks
- Payment failures
- Refund handling where supported
- Order/payment consistency

Never trust payment-success information supplied only by the browser.

The provider should be selected during Phase 9 based on country support, business requirements, fees, settlement, compliance, and webhook/refund capabilities.

---

## 11.9 Messaging

Support:

- Buyer/seller conversations
- Message history
- Read/unread state
- Notifications
- Reporting/abuse controls

Start with standard HTTP APIs. Add WebSockets later if real-time requirements justify them.

---

## 11.10 Reviews

Eligible completed transactions should support:

- Rating
- Optional review text
- Review timestamp
- Review moderation/reporting

The backend must verify that the user is eligible to review the transaction.

---

## 11.11 Notifications

Notifications can cover:

- Order updates
- Payment updates
- Listing status
- New messages
- Reviews
- Administrative notices

Delivery should be abstracted so additional channels can be added later.

---

## 11.12 Reports

Users can report:

- Listings
- Users
- Messages
- Transaction problems

Reports should contain:

- Reporter
- Target
- Reason
- Description
- Status
- Admin notes
- Timestamps

---

## 11.13 Admin

Admin tools should support:

- User management
- Listing moderation
- Order inspection
- Payment inspection
- Report management
- Review moderation
- Platform statistics
- Administrative actions
- Audit logs

Sensitive administrative actions must be auditable.

---

# 12. Security Requirements

The application must include a security strategy covering:

- Password hashing
- Authentication
- Authorization
- Input validation
- SQL injection prevention
- XSS prevention
- CORS
- Rate limiting
- Security headers
- Secure cookies/tokens
- File-upload validation
- Access control
- Admin protection
- Secrets management
- Audit logging
- Abuse prevention

Never expose:

- Password hashes
- Private credentials
- Payment secrets
- Internal tokens
- Sensitive transfer information

through public APIs.

---

# 13. File and Image Storage

Production uploads should not be permanently stored inside application containers.

Prepare an abstraction for:

- S3-compatible object storage
- Cloudinary
- Another managed storage provider

Uploads should eventually support:

- File type validation
- Size limits
- Safe storage keys
- Image optimization
- Access control
- CDN delivery

---

# 14. Performance Requirements

The application should support:

- Pagination
- Proper database indexes
- Efficient SQL queries
- Lazy loading where appropriate
- Image optimization
- CDN delivery
- API response consistency
- Caching where useful
- Background processing for expensive tasks

Avoid premature infrastructure complexity.

---

# 15. Scalability Strategy

Use progressive scaling:

```text
Stage 1
Modular Monolith
        ↓
Stage 2
Multiple FastAPI Instances
        ↓
Stage 3
Redis Caching
        ↓
Stage 4
Background Workers
        ↓
Stage 5
Object Storage + CDN
        ↓
Stage 6
Database Optimization / Read Replicas
        ↓
Stage 7
Selective Service Extraction if justified
```

Do not begin with microservices.

---

# 16. API Standards

All APIs should use:

```text
/api/v1
```

Examples:

```text
/api/v1/auth/login
/api/v1/users/me
/api/v1/listings
/api/v1/listings/{listing_id}
/api/v1/orders
/api/v1/payments
/api/v1/reviews
```

Use consistent:

- HTTP status codes
- Request schemas
- Response schemas
- Error responses
- Pagination
- Filtering
- Sorting

---

# 17. Testing Strategy

## Unit Tests

Test:

- Business logic
- Validation
- Services
- Utilities

## Integration Tests

Test:

- API endpoints
- Database operations
- Authentication
- Orders
- Payments

## Frontend Tests

Test:

- Components
- Forms
- Features
- Routes

## End-to-End Tests

Critical flows:

```text
Register
  ↓
Login
  ↓
Browse marketplace
  ↓
View listing
  ↓
Create listing
  ↓
Place order
  ↓
Payment
  ↓
Order completion
  ↓
Review
```

---

# 18. Development Rules

Every phase must:

1. Preserve the approved architecture.
2. Avoid unnecessary rewrites.
3. Avoid breaking completed functionality.
4. Keep feature modules isolated.
5. Add tests for important functionality.
6. Update documentation when necessary.
7. Use environment variables.
8. Never commit secrets.
9. Keep frontend and backend responsibilities separated.
10. Verify the phase before moving to the next phase.

When using Antigravity, build **one phase at a time**. Do not ask it to implement the entire marketplace in a single prompt.

---

# 19. PHASED DEVELOPMENT PLAN

## PHASE 1 — Foundation

### Goal

Create a clean, runnable monorepo.

### Build

- Root repository
- React + Vite
- FastAPI
- PostgreSQL configuration
- SQLAlchemy foundation
- Alembic foundation
- Environment configuration
- Basic React routing
- FastAPI `/health`
- Docker Compose foundation
- Git configuration
- README
- Initial backend test

### Do Not Build

- Real authentication
- Orders
- Payments
- Marketplace business logic
- Redis
- Messaging

### Completion Criteria

```text
Frontend runs
Backend runs
PostgreSQL configuration works
/health works
Basic routes work
Docker configuration validates
Test passes
README exists
```

---

# PHASE 2 — Frontend Design System

### Goal

Create the reusable UI foundation before implementing business features.

### Build

- Global layout
- Header
- Footer
- Navigation
- Buttons
- Inputs
- Selects
- Cards
- Modal
- Dropdown
- Toast/alert
- Loading states
- Empty states
- Error states
- Responsive breakpoints
- Typography
- Spacing system
- Theme variables

### Pages

Create initial UI shells for:

```text
Home
Marketplace
Login
Register
Listing Details
Buyer Dashboard
Seller Dashboard
Admin Dashboard
```

### Completion Criteria

All pages are navigable and visually consistent.

---

# PHASE 3 — Database Architecture

### Goal

Design and implement the initial relational database.

### Build

- PostgreSQL schema
- SQLAlchemy models
- Alembic migrations
- Relationships
- Foreign keys
- Unique constraints
- Indexes
- Timestamps
- Status fields
- Database seed strategy

### Core tables

```text
users
user_profiles
accounts
account_images
listings
orders
payments
reviews
favorites
conversations
messages
notifications
reports
audit_logs
```

### Completion Criteria

Database can be created from migrations on a clean environment.

---

# PHASE 4 — FastAPI Backend Foundation

### Goal

Build the reusable backend architecture.

### Build

- API versioning
- Router registration
- Dependency injection
- Error handling
- Response structure
- Request validation
- Logging
- Request IDs
- Database session management
- Repository pattern
- Service layer
- API documentation

### Completion Criteria

Backend has a stable foundation for all business modules.

---

# PHASE 5 — Authentication & Authorization

### Goal

Implement secure user access.

### Build

- Registration
- Login
- Logout
- Password hashing
- Authentication
- Token/session handling
- Password reset foundation
- Email verification foundation
- Roles
- Permissions
- Protected routes
- Protected API endpoints

### Roles

```text
BUYER
SELLER
ADMIN
```

### Completion Criteria

Users can securely authenticate and access only authorized resources.

---

# PHASE 6 — Users, Accounts & Seller Profiles

### Goal

Create the user and account-management foundation.

### Build

- User profile
- Seller profile
- Account entity
- Account attributes
- Account images
- Profile editing
- Account ownership rules
- Image upload abstraction

### Completion Criteria

Authenticated sellers can create/manage account data without exposing private information.

---

# PHASE 7 — Marketplace & Listings

### Goal

Build the core marketplace.

### Build

- Create listing
- Edit listing
- Delete/archive listing
- Listing status
- Listing details
- Image gallery
- Marketplace grid
- Listing cards
- Seller information
- Price display
- Draft listings

### Completion Criteria

Seller can create a listing and buyer can view it through the marketplace.

---

# PHASE 8 — Search, Filters & Discovery

### Goal

Make listings discoverable.

### Build

- Search
- Filters
- Sorting
- Pagination
- URL-based filter state
- Database indexes
- Query optimization
- Empty results
- Search loading/error states

### Completion Criteria

Users can efficiently find listings using supported marketplace criteria.

---

# PHASE 9 — Orders & Payments

### Goal

Implement the transaction lifecycle.

### Build

- Checkout
- Order creation
- Order states
- Payment initiation
- Payment provider integration
- Webhooks
- Payment verification
- Payment failure handling
- Refund flow where supported
- Transaction records

### Important

The browser must never be the source of truth for payment success.

### Completion Criteria

A supported transaction can move safely through the configured payment and order states.

---

# PHASE 10 — Buyer Dashboard

### Goal

Build the complete buyer experience.

### Build

- Buyer dashboard
- Orders
- Order details
- Favorites
- Messages
- Notifications
- Profile
- Settings
- Review history
- Reports/support

### Completion Criteria

Buyer can manage the complete supported marketplace experience from one dashboard.

---

# PHASE 11 — Seller Dashboard

### Goal

Build the complete seller workflow.

### Build

- Seller dashboard
- Listings
- Create/edit listing
- Listing status
- Orders
- Sales history
- Messages
- Reviews
- Notifications
- Seller settings
- Profile

### Completion Criteria

Seller can manage listings and supported sales workflows from one dashboard.

---

# PHASE 12 — Favorites, Reviews & Messaging

### Goal

Build marketplace engagement features.

### Build

Favorites:

- Add
- Remove
- List favorites

Reviews:

- Eligibility
- Rating
- Review text
- Review history
- Moderation/reporting

Messaging:

- Conversations
- Messages
- Read/unread
- Basic notifications
- Reporting

### Completion Criteria

Eligible buyers and sellers can interact through supported engagement features.

---

# PHASE 13 — Notifications & Background Jobs

### Goal

Move asynchronous work out of request/response flows.

### Build

- Redis
- Background job system
- Notification jobs
- Email jobs
- Image processing jobs
- Cleanup jobs
- Retry strategy
- Job logging

### Completion Criteria

Long-running or non-critical tasks do not unnecessarily block API requests.

---

# PHASE 14 — Admin & Moderation

### Goal

Provide platform administration.

### Build

- Admin authentication
- User management
- Listing moderation
- Report management
- Review moderation
- Order inspection
- Payment inspection
- Platform statistics
- Administrative actions
- Audit logs

### Completion Criteria

Administrators can safely manage platform operations.

---

# PHASE 15 — Security Hardening

### Goal

Perform a dedicated security pass.

### Review

- Authentication
- Authorization
- Password security
- Input validation
- SQL injection
- XSS
- CORS
- CSRF where applicable
- Rate limiting
- File uploads
- API abuse
- Admin access
- Secrets
- Security headers
- Dependency vulnerabilities
- Audit logs

### Completion Criteria

Security issues discovered during review are fixed or documented with a mitigation plan.

---

# PHASE 16 — Performance & Scalability

### Goal

Prepare the platform for increased traffic.

### Build/Optimize

- Database indexes
- Query optimization
- Pagination
- Redis caching
- CDN
- Image optimization
- API performance
- Connection pooling
- Background workers
- Horizontal FastAPI scaling
- Load balancing
- Static asset caching

### Completion Criteria

Performance is measured rather than optimized based only on assumptions.

---

# PHASE 17 — Testing & Quality Assurance

### Goal

Validate the complete system.

### Build

- Unit tests
- Integration tests
- API tests
- Frontend tests
- End-to-end tests
- Authentication tests
- Authorization tests
- Payment tests
- Error-path tests
- Load/performance tests
- Regression tests

### Critical workflows

```text
Registration
Login
Listing creation
Listing search
Listing purchase
Payment
Order completion
Review
Reporting
Admin moderation
```

---

# PHASE 18 — Docker & Production Deployment

### Goal

Create reproducible deployment infrastructure.

### Build

- Production Dockerfiles
- Docker Compose
- Nginx
- Environment management
- Production database configuration
- Object storage
- CDN
- HTTPS
- Domain configuration
- Health checks
- CI/CD

### Completion Criteria

The application can be deployed using documented production procedures.

---

# PHASE 19 — Monitoring & Operations

### Goal

Make the production platform observable.

### Build

- Structured logs
- Error tracking
- Metrics
- API latency monitoring
- Database monitoring
- Infrastructure monitoring
- Health checks
- Alerts
- Backup strategy
- Recovery documentation

### Completion Criteria

Operational failures can be detected, investigated, and recovered from.

---

# PHASE 20 — Production Launch Readiness

### Goal

Perform the final launch review.

### Checklist

- Security review
- Terms/policy review
- Payment-provider requirements
- Privacy requirements
- User-facing policies
- Error handling
- Database backups
- Monitoring
- Performance
- SEO
- Mobile responsiveness
- Accessibility
- Production environment
- Domain
- HTTPS
- CI/CD
- Rollback procedure
- Support process

Only launch after all applicable requirements are verified.

---

# 20. Antigravity Development Workflow

For every phase, use this workflow:

```text
PRD
 ↓
Phase Prompt
 ↓
Antigravity Implementation
 ↓
Run / Test
 ↓
Review
 ↓
Fix Issues
 ↓
Confirm Phase Complete
 ↓
Git Commit
 ↓
Next Phase
```

Do not give Antigravity the entire implementation task at once.

Each phase prompt should explicitly state:

- Current architecture
- Current phase
- What to build
- What not to build
- Existing files that must not be unnecessarily rewritten
- Coding standards
- Security requirements
- Testing requirements
- Completion criteria
- Stop condition

---

# 21. Git Strategy

Use meaningful commits after each stable milestone.

Example:

```text
feat: initialize project foundation
feat: add frontend design system
feat: add database schema
feat: add fastapi architecture
feat: add authentication
feat: add account management
feat: add marketplace listings
feat: add search and filters
feat: add orders and payments
feat: add buyer dashboard
feat: add seller dashboard
feat: add messaging and reviews
feat: add background jobs
feat: add admin moderation
security: harden application
perf: optimize marketplace
test: add integration and e2e coverage
chore: prepare production deployment
```

---

# 22. Definition of Done

A phase is complete only when:

- Required functionality is implemented.
- Existing functionality still works.
- Code follows the approved architecture.
- No unnecessary duplicate implementation exists.
- Tests pass.
- Important errors are handled.
- Documentation is updated where required.
- Environment configuration is documented.
- The application can be run using documented commands.
- The phase's completion criteria are satisfied.

Do not automatically begin the next phase.

---

# 23. Final Product Architecture

The expected long-term architecture is:

```text
                         USERS
                           |
                           v
                    CLOUDFLARE / CDN
                           |
                           v
                         NGINX
                           |
             +-------------+-------------+
             |                           |
             v                           v
       REACT + VITE                  FASTAPI
             |                           |
             |                  +--------+--------+
             |                  |                 |
             |                  v                 v
             |             PostgreSQL           Redis
             |                  |                 |
             |                  |           Background Jobs
             |                  |
             |                  v
             |            Object Storage
             |                  |
             +------------------+
```

Backend:

```text
FastAPI
  |
  +-- Auth
  +-- Users
  +-- Accounts
  +-- Listings
  +-- Orders
  +-- Payments
  +-- Reviews
  +-- Favorites
  +-- Messages
  +-- Notifications
  +-- Reports
  +-- Admin
```

---

# 24. Phase Summary

| Phase | Main Deliverable |
|---|---|
| 1 | Project Foundation |
| 2 | Frontend Design System |
| 3 | Database Architecture |
| 4 | FastAPI Backend Foundation |
| 5 | Authentication & Authorization |
| 6 | Users, Accounts & Seller Profiles |
| 7 | Marketplace & Listings |
| 8 | Search, Filters & Discovery |
| 9 | Orders & Payments |
| 10 | Buyer Dashboard |
| 11 | Seller Dashboard |
| 12 | Favorites, Reviews & Messaging |
| 13 | Notifications & Background Jobs |
| 14 | Admin & Moderation |
| 15 | Security Hardening |
| 16 | Performance & Scalability |
| 17 | Testing & QA |
| 18 | Docker & Production Deployment |
| 19 | Monitoring & Operations |
| 20 | Production Launch Readiness |

---

# 25. Product Principle

Build the platform in small, verified increments.

**Do not optimize for maximum infrastructure on day one. Optimize for a clean architecture that can scale when real requirements appear.**

**Do not use microservices initially.**

**Do not add infrastructure merely because it is available.**

**Do not let later phases rewrite the architecture unnecessarily.**

**Each phase must produce a working, testable improvement to the product.**
