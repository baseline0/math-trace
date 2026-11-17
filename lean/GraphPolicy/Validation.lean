import Lean.Data.Json
import GraphPolicy.Basic

open Lean

namespace GraphPolicy.Validation

/-- Single benchmark run record from empirical evaluation.
    Metrics use scaled integer values (basis points / PPM) to avoid IEEE Float issues
    and ensure deterministic compile-time evaluation via native_decide. -/
structure BenchmarkRun where
  runId : String
  isFixture : Bool
  overheadBp : Int
  thresholdPpm : Int
  nodesEvaluated : Nat
  edgesEvaluated : Nat
  deriving FromJson, ToJson, Repr, DecidableEq

/-- Ingest empirical results exported by Python at compile time. -/
def rawBenchmarkJson : String := include_str ".." / ".." / "artifacts" / "benchmarks.json"

/-- Parse the raw JSON string into benchmark run records. -/
def parseBenchmarkRuns : Except String (List BenchmarkRun) := do
  let j ← Json.parse rawBenchmarkJson
  fromJson? j

/-- Theoretical upper bound on algorithm overhead: 2.0x (20,000 basis points). -/
def maxOverheadBp : Int := 20000

/-- Theoretical lower bound on error threshold: 1.0% (10,000 ppm). -/
def minThresholdPpm : Int := 10000

/-- Verify all runs satisfy the theoretical bounds. -/
def checkAllBounds : Bool :=
  match parseBenchmarkRuns with
  | Except.ok runs =>
      !runs.isEmpty &&
      runs.all fun r => r.overheadBp ≤ maxOverheadBp && r.thresholdPpm ≥ minThresholdPpm
  | Except.error _ => false

/-- Check if all runs are live (not fixture data). -/
def checkAllLive : Bool :=
  match parseBenchmarkRuns with
  | Except.ok runs =>
      !runs.isEmpty && runs.all fun r => !r.isFixture
  | Except.error _ => false

/-- COMPILE-TIME GATE: Verified empirical bounds.
    Fails to compile if any benchmark run violates theoretical overhead or threshold bounds. -/
theorem empirical_data_valid : checkAllBounds = true := by
  native_decide

end GraphPolicy.Validation
