## ADDED Requirements

### Requirement: Re-confirm page identity immediately before writing

Verifying navigation only at the point it completes cannot protect against anything that disturbs the
session afterwards. Before issuing the first `execset` of an operation, the service SHALL re-select
the target page at its own `(branchnr, level)` coordinates and SHALL re-confirm the page title
identifies the intended circuit and page.

If the re-confirmation fails, the service SHALL NOT issue any write and SHALL surface a 502.

#### Scenario: Position intact between navigation and write
- **WHEN** nothing has disturbed the session since navigation completed
- **THEN** re-selecting the target coordinates returns the same page, the title matches, and the write proceeds

#### Scenario: Position disturbed between navigation and write
- **WHEN** the device's navigation position has moved since navigation completed
- **THEN** re-selecting the target coordinates returns a page whose title does not match, and the service SHALL abort without issuing any `execset`

## MODIFIED Requirements

### Requirement: Serialise WEB-RC navigation across circuits

The HPM web server maintains a single per-session, stateful navigation context. The service SHALL serialise **all** requests to the device through a single lock — WEB-RC navigation, `info.rsp` range reads, `execset.rsp` writes, and the `v*.rsp` status view pages alike — so that no request can interleave with another operation on the shared session.

Serialisation SHALL be determined by the fact that a request shares the session, not by whether it is a WEB-RC request. In particular, status reads SHALL hold the lock for the whole set of view-page fetches they perform, because a status read that interleaves between a verified navigation and its dependent writes causes those writes to land on the wrong parameter.

Within a single status read, the individual view-page fetches MAY proceed concurrently with each other, since they perform no navigation.

#### Scenario: Concurrent HC1 and HC2 navigation does not interleave
- **WHEN** requests that navigate to HC1 and HC2 WEB-RC pages arrive concurrently
- **THEN** the service serialises them through one lock, so each navigation re-establishes its full path from root without the other corrupting the shared session context, and each returns data for the correct circuit

#### Scenario: Status read does not interleave with a write operation
- **WHEN** a status read is requested while a WEB-RC write operation is between its navigation and its `execset` writes
- **THEN** the status read SHALL wait for the write operation to complete, and SHALL NOT issue any request to the device in the interim

#### Scenario: Write operation does not interleave with a status read
- **WHEN** a WEB-RC write is requested while a status read is in progress
- **THEN** the write SHALL wait for the status read to finish before beginning its navigation
