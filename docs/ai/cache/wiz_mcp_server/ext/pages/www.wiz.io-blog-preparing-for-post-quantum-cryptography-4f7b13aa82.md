---
url: https://www.wiz.io/blog/preparing-for-post-quantum-cryptography
source_name: blog_product
fetched_at: 2026-03-02T17:52:04Z
published_at: 2026-01-08T09:51:34-05:00
extraction_mode: static_fetch
content_hash: 73cae3646dca
---

# Preparing for Post-Quantum Cryptography | Wiz Blog

Quantum readiness, or being prepared for Post-Quantum Cryptography (PQC), is the concept of ensuring your data and communications remain confidential and trusted even when quantum computers become capable of breaking common encryption protocols in use today.  This post will discuss what the risks are, what you can do to prepare for post-quantum cryptography, and what Wiz is doing.  In order to help Wiz customers create an inventory for PQC migration, we’ve created the “Wiz for Post-Quantum Cryptography Security Framework” where we have added detections for relevant encryption.
Background on quantum computers
The concept of a quantum computer was first proposed in 1980.  They are theoretically better at solving some types of problems than traditional computers, and in 1994,
Shor’s algorithm
was invented which would allow a sufficiently capable quantum computer to factor prime numbers (ie. break RSA encryption) much faster than a traditional computer would ever be able to. Similar algorithms were also proposed to solve the problems that other asymmetric cryptography and key exchange use (ex. elliptic curve cryptography, such as X25519).
It wasn’t until 1998 that a quantum computer was actually created, but it was extremely minimal as a proof-of-concept. Today, quantum computers have become much more accessible. For example, you can use quantum computers on cloud providers such as AWS’s
Braket
service.  However, they are still not powerful enough to compete with traditional computers, at least on the problem of breaking cryptography.
One measure of quantum computing capability is the number of qubits. The quantum computers with the most qubits have thousands of qubits, but that is not the only criteria for determining how capable a quantum computer is. For example, Google announced their new
Willow
chip in December 2024, which has only 105 qubits, but handles errors better than other quantum computers.  Similarly, Amazon announced their
Ocelot
chip and Microsoft announced their
Majorana
chip, both in February 2025, which have fewer qubits, but again have better error handling. Due to the difficulty in comparing quantum computers, there isn’t a good way of evaluating how much progress has been made toward having a Cryptographically Relevant Quantum Computer (CRQC) which could break RSA-2048, or when we should expect one to be built. The number of qubits needed to break RSA-2048 is currently believed to be less than a million noisy qubits and a week of work according to one
paper
, so we are still orders of magnitude away.   The day when a quantum computer does arrive that breaks RSA-2048 is referred to as Q-Day. Larger key sizes and other asymmetric cryptography are also at risk.
Experts have varying levels of expectations on when (or if) a Cryptographically Relevant Quantum Computer will exist, with one set of
predictions
believing a likelihood of 25% for one to exist in ten years, and 60% likelihood for it to exist in 20 years.
One datapoint I found surprising is that the biggest number that is generally agreed was successfully factored by a quantum computer thus far is the number
21
(yes, 7 multiplied by 3).  This was done in 2012.  Other claims for larger numbers have a lot of contention regarding how much classical computers were relied on, and therefore are not good indicators of the progress toward a CRQC. Even the claim of factoring the number 21 has
contention
around how much prior knowledge of the factors was involved, and therefore some claim the largest number factored is 15, done in 2001. While significant progress has been made in the development of the technology, being able to leverage it for practical applications has been slow.
Should you be worried?
The short answer is that a Cryptographically Relevant Quantum Computer (CRQC) does not exist today that can break encryption, but one may exist at some point in the future, and there are steps you should begin taking now to prepare for that.   As this threat has been known for decades, there has been work done in creating new cryptographic standards that can withstand attacks by quantum computers.  You should begin identifying what cryptographic mechanisms you are using that would be vulnerable, and where, and begin developing a migration plan.
One reason you should start preparing today is that advances in quantum computers could occur suddenly and force you to migrate quickly to account for that. Another reason is that an attacker could harvest encrypted data today and then wait until a CRQC exists to decrypt it. This is referred to as the Harvest Now, Decrypt Later (HNDL) threat.  Another big concern (primarily outside of cloud environments) are cryptographic systems with long life times that cannot be easily updated. Due to the national intelligence and geopolitical advantages of being the first to break cryptography with a quantum computer, the public may only find out about it well after a country is able to achieve this milestone.
Whether you are worried about these risks, or whether you are optimistic or not about a Cryptographically Relevant Quantum Computer ever existing, you may still be required to migrate your encryption mechanisms, as I’ll explain shortly, and
luckily some of the most important things you can do are easy!
What is the current status of Post-Quantum Cryptography Standards?
Since 2016, a competition has been run by NIST to determine what new cryptographic mechanisms should be used.  On August 13, 2024,
NIST announced 3 standards
, which means they’ve decided on what should replace existing cryptographic mechanisms. Now that the path forward has been decided, people should begin working toward migrating systems to these standards.
The standards that have been developed by NIST are as follows:
NIST Standard
Old name
New name
Problem it is based on
Use case
FIPS 203
CRYSTALS-Kyber
ML-KEM
Module-Lattice
Key-Encapsulation Mechanism
FIPS 204
CRYSTALS-Dilithium
ML-DSA
Module-Lattice
Digital Signature Algorithm
FIPS 205
Sphincs+
SLH-DSA
Stateless Hash
Digital Signature Algorithm. Alternative to FIPS 204, that uses a more mature math foundation, but produces larger and slower signatures.
FIPS 206 (in progress)
FALCON
FN-DSA
Fast-Fourier transform over NTRU-Lattice
Digital Signature Algorithm. Backup to FIPS 204 and 205, produces smaller signatures but at increased complexity.
The timeline set forth by a
National Security Memorandum
from 2022 is to complete this within a decade of the publication of the standards, which means this migration should occur by 2035 for the US federal government.  An
Executive Order
also requires support for TLS 1.3 by 2030 as part of the transition to PQC, as that is the only version of TLS that will support these standards. Federal agencies have already been
instructed
to provide annual inventories of systems that must be migrated.
The US government is investing heavily in quantum research in an effort to accelerate development. The White House issued a
memorandum
directing agencies to prioritize research and development dollars towards quantum computing projects last year. Additionally, the President recently signed an
Executive Order
launching the
Genesis Mission
, “a national initiative to build the world's most powerful scientific platform.” One of the core areas it will seek to accelerate is “quantum information science.”
The Dutch General Intelligence and Security Service published a comprehensive document titled
The PQC Migration Handbook
in December 2024 that has a lot of valuable information including discussion of the efforts from other countries and organizations to make PQC standards.
Well beyond the US, other nations are also setting requirements for transitioning key systems to quantum resistant cryptographic algorithms. The UK’s NCSC has
stated
inventories and a migration plan must be completed by 2028, with full transition by 2035.
Japan
and
Canada
are also seeking full transition by 2035, while
Australia
is seeking to complete transition by 2030. The
European Union
is targeting that critical infrastructure be transitioned to PQC by 2030, with full transition by 2035.
What needs to be upgraded?
Only asymmetric cryptography is being replaced (ex. RSA, ECDH, ECDSA, and EdDSA).  Symmetric encryption and hashing are not as vulnerable.  Quantum computers are more capable than traditional computers for attacking symmetric encryption (via something called Grover’s quantum algorithm), but according to the NIST
FAQ
on PQC, AES-128 is quantum resistant. For hashing, SHA-2 is
recommended
for PQC. Note that you may need to evaluate your specific use case as these statements are given by different organizations as general guidance.
We believe migration plans should be broken into 3 parts:
Inventory what needs to be migrated.
Migrate TLS and SSH key exchange functionality.
Migrate everything else.
I’ll talk more about how to create an inventory in a moment, but let’s look at that second step. I believe this should be the initial focus after an inventory because it is not only urgent, but it is also easy! This step is urgent because it mitigates the Harvest Now, Decrypt Later risk for those systems, and it’s easy because it just involves upgrading software or setting a configuration.
Upgrading things so that PQC is used in key exchanges is so easy that you might already be supporting it.  We scanned the top 1 million domains (using
Cloudflare’s list
, which includes domains beyond those hosted on Cloudflare), and found that 84% of the accessible domains support TLS 1.3, which is needed for the PQC key exchanges.  45% of the total accessible domains support the PQC key exchanges.
Example
Let’s take a server with OpenSSH running as an example.  Imagine you installed OpenSSH a few years ago and a dozen people created RSA key pairs for their authentication to it (let’s ignore that there are probably better ways of accomplishing whatever it is we set this up for).  There are two important things you’ll want to do to upgrade this for PQC compliance.  The first is to upgrade the OpenSSH server to the latest version so it uses PQC for the key exchange.  The second is to regenerate new key pairs using a PQC compliant signature algorithm.
The first step is a simple upgrade of the server and the clients (with no dependencies on ordering) and now all communication is protected against Harvest Now Decrypt Later risks.  You do NOT need to generate new PQC key pairs in order to be protected against that risk.  The RSA key pairs are used in the authentication, which happens after an encrypted session has already been set up that is protected with PQC.  The authentication using the RSA key pairs is only at risk if an attacker obtains a CRQC before you start using new key pairs, so it is not as urgent.  If you wait to upgrade OpenSSH though then the attacker might be collecting the traffic now and that traffic will be readable by the attacker once they have a CRQC.
The second step of generating new key pairs is much more troublesome to do.  The first problem you’ll run into is OpenSSH does not currently support a PQC algorithm for authentication, so you can’t perform this step even if you wanted to.  But once OpenSSH does support ML-DSA, you’ll need to get everyone to generate and start using those new keys, and get rid of the old ones, which is messier.  Migrating keys is more difficult than simply upgrading software.  So this part of the migration falls in the “everything else” category.  Although a lot of software has now added support for TLS and SSH key exchange functionality, very little other PQC support exists today.
How to create an inventory for PQC migration
In order to help Wiz customers create an inventory for PQC migration, we’ve created the “Wiz for Post-Quantum Cryptography Security Framework” where we have added detections for relevant encryption. This capability is sometimes referred to as an Automated Cryptography Discovery and Inventory (ACDI) tool with one form of output known as a Cryptographic Bill of Materials (CBOM).
Screenshot of the “Wiz for Post-Quantum Cryptography Security Framework” dashboard
Identifying quantum-vulnerable cryptography is a complex challenge that requires visibility across your entire infrastructure. Wiz addresses this by providing a unified approach to detecting at-risk encryption.
1. Cloud Infrastructure
Wiz surfaces cryptographic metadata directly within your inventory, providing a Cloud services cryptographic Bill of Materials. This allows you to audit cloud-native encryption at scale:
TLS Termination
: Identify cloud services including Load Balancers and Web Services using legacy protocols that require an upgrade to PQC-ready standards.
Key Management
: Audit key configurations to ensure key lengths and algorithms meet future-proof security requirements.
Deep Visibility
: Instantly filter resources by encryption algorithm, key length, and ownership to prioritize remediation of assets that fall short of modern standards.
2. How Wiz Detects Your Cryptographic Risks
To eliminate blind spots in your active environment, Wiz leverages different scanning methods:
Dynamic Scanning (External Network Scanning)
: Proactively scan public-facing services to identify active cryptographic protocols. Detection focuses on identifying
weak SSH Key Exchange (KEX)
methods.
Secret Scanning
: Automatically detect cryptographic artifacts, including SSH private keys and TLS certificates, stored across your cloud environment.
Host Configuration Auditing
: Wiz evaluates post-quantum readiness by inspecting local configuration files (e.g., SSH configs, system-wide crypto policies, and web server settings) to verify if quantum-safe hybrid cryptography is correctly implemented.
3. Future-Proofing Your Strategy (Coming Soon)
Wiz is continuously expanding its PQC roadmap to provide even deeper visibility and automation:
PQC-Aware Code Scanning
: Identify references to cryptography usage directly within source code, such as
AWS SDK configurations
that need to be optimized for PQC, before they are ever deployed.
Software Lifecycle Tracking
: Easily identify PQC supported vs. non-supported software based on specific components and version numbers. This will allow you to see exactly when a library or application begins to support PQC-ready standards.
What does PQC support mean?
At Wiz, we are defining PQC support to mean that the NIST standards are in use, or can be used, whether through negotiation or as part of hybrid cryptography.  Let’s dive more into each of these constraints.
The NIST standards came out in August 2024, so any PQC capabilities offered prior to that were experimental, and thus not what we view as PQC compliant. Further, our customers have asked to ensure they are adhering to the NIST PQC standards, so the use of other PQC algorithms are viewed as not compliant.
When I mention being supported through negotiation, I’m referring to something like TLS session negotiation, where multiple ciphers and key exchange mechanisms can be used for backward compatibility.   A purist may want to only support PQC, but this is not reasonable today for many use cases, so what we view as a PQC compliant environment may still have some evidence of classical cryptography due to that ability to negotiate for backwards compatibility.
Many deployments of PQC are doing so through hybrid cryptography where both PQC and classical cryptography are being used together.  This is being done in case one or the other is broken, such that the data will remain secure. Although the new PQC standards are believed to be secure, they (and the math behind them), have not been battle tested as much as the existing classic cryptography. An example of this is AWS’s TLS policies use this strategy as is evidenced in the PQC-supported quantum-safe key exchanges X25519MLKEM768 and SecP256r1MLKEM768 which are using the PQC standard ML-KEM 768, along with an additional classic cryptography standard.  Again, under this scheme, classical cryptography is being used, but we still view this as PQC compliant.
To give an example of how these constraints play out, OpenSSH began defaulting to sntrup761x25519-sha512 (a hybrid PQC key exchange) since release 9.0 (April 2022), and had supported a version of it as early as OpenSSH 8.0 (April 2019), but NIST chose not to accept that algorithm, so we don’t view OpenSSH as compliant unless it uses at least release OpenSSH 10.0 (April 2025), at which point it began defaulting to mlkem768x25519-sha256.
When migrating to PQC, a term that often comes up is “cryptographic agility”, which is the ability to switch between cryptographic primitives, in case one is discovered to be vulnerable. An example often pointed to with regard to this concept is during the NIST competition, one proposal known as
SIKE
was found to be insecure. This proposal had not been standardized and so the early identification of the insecurity can be pointed as a success of the competition, but it had made it to the final round of the competition.  As a result of the apparent future of SIKE, it was used as part of an
early experimental deployment of PQC
by Cloudflare and Google Chrome, but was done using hybrid cryptography.  This can be viewed as an example of the success of this hybrid strategy because the communications were not at risk due to traditional cryptography still being used.  For this reason, hybrid cryptography is a related strategy to consider when discussing cryptographic agility.
Testing your web services
In order to make it easier for everyone to confirm whether they are using PQC compliant key exchanges on their HTTPS services, we’ve created the free service
wiz.io/pqc-tester
.
PQC tester demonstration
Conclusion
You should begin preparing for quantum readiness today by creating an inventory of your use of at-risk cryptography.  Wiz can help and we’re adding more ways of identifying at-risk cryptography for our customers.
Tags
#
Product
#
Research