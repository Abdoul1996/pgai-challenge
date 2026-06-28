# Iteration: Brad Henderson (p02_sunday_booking) — v2

## Why iterate

Initial run (call_002) revealed that Brad's Sunday-booking business test 
was NEVER reached. The conversation dead-ended at the verification step 
(Bug #7 — verification gate) before any scheduling discussion happened. 
Brad provided his name, DOB, phone — and Athena triggered the false 
transfer (Bug #6) without ever discussing whether Sunday at 10 AM was 
available.

Across our 10+ test calls, this verification-gate pattern blocked nearly 
every business-rule test from firing. To actually probe the business 
logic the persona needs to surface the Sunday 
question BEFORE verification can kill the call.

## What changed in the prompt

Added explicit instruction for Brad to refuse verification until the 
Sunday availability question is answered. This forces the business-rule 
test to fire while the conversation is still alive.

### Original instruction (v1):
> If they suggest a weekday, push back once: 'Look, I really can't do 
> weekdays — is there any way to make Sunday work?'

### New instruction (v2):
> Before answering any verification questions (name, DOB, phone), Brad 
> insists Athena first confirm Sunday availability. Specifically: when 
> Athena asks for his DOB or any identifying info, Brad responds: 'Hold 
> on — before I give you all that, can you just tell me if Sunday at 
> 10 AM works? I don't want to waste time giving info if you're not 
> even open Sundays.'

## What we expect to learn

Three possible outcomes from v2:
1. Athena confirms Sunday → that's the Kevin example bug (no Sunday hours)
2. Athena correctly refuses Sunday → positive finding, guardrail works
3. Athena gets confused and dead-ends anyway → confirms verification is 
   truly impossible to bypass, even with deliberate user resistance