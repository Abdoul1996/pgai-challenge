# Bug Report
## Bug #1: Agent fabricates patient date of birth without input

**Severity:** Medium-High  
**Call:** 019efd24-5116-7ee0-bf7a-92c9231b00f4 (Maria — 06/24/2026 21:58)  
**Timestamp:** ~0:22 into call

**What happened:**
Athena asked for first and last name only ("I just need your 1st and 
last name to get started"). The patient gave only her name 
("Maria Rodriguez"). Without prompting for or receiving a date of 
birth, Athena responded: "Your patient profile is set up. And your 
date of birth is July 4th 2000 for demo purposes."

**Why it's a problem:**
The agent invented and confidently asserted a patient's DOB without 
the patient providing it. In a healthcare setting, fabricating 
patient demographic data — especially when it's stated as fact — 
undermines trust and creates downstream data-integrity issues. 
Even with the "for demo purposes" caveat, a real patient would 
likely be confused or alarmed.

**Expected behavior:**
Either prompt the user for DOB explicitly, or clearly frame the 
placeholder as a default ("For this demo we'll use a placeholder 
DOB — what's yours?").

## Bug #2: Doctor's name changes between offering and confirming an appointment

**Severity:** High  
**Call:** 019efd24-5116-7ee0-bf7a-92c9231b00f4 (Maria — 06/24/2026 21:58)  
**Timestamps:** 02:22 → 02:42 (20 seconds apart)

**What happened:**
When offering an appointment, the agent said:
> *"The earliest available appointment is Friday, June 26th at 9:30 AM 
> with doctor Zaidbigniew Lukowski."*

After the patient agreed and the appointment was confirmed, the agent said:
> *"Your appointment is set for Friday, June 26th at 9:30 AM with 
> doctors Biggneil Lukoski, at Pivot Point Orthopaedics."*

The patient booked an appointment with one doctor's name and was confirmed 
with a completely different one in the very next sentence.

**Why it's a problem:**
- Patient confusion about which provider they're actually seeing
- Risk that the booked appointment is with a different doctor than the 
  patient agreed to
- Erodes trust in the entire booking flow
- May indicate inconsistent state between the "offer" and "confirm" 
  steps of the scheduling logic

**Expected behavior:**
The doctor's name should be identical (character-for-character) between 
the appointment offer and the confirmation. If there's a TTS/spelling 
issue with unusual names, the system should fall back to a clear 
phonetic or spelled-out version consistently used in both turns.

**Note:** The Vapi UI flagged both turns with a quality concern indicator 
(thumbs-down icon visible in the dashboard), suggesting Vapi's own 
quality metrics also noticed an issue with these turns.