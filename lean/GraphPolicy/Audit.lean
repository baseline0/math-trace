import GraphPolicy.Validation
import GraphPolicy.Separation

namespace GraphPolicy.Audit

open GraphPolicy.Validation

/-- COMPILE-TIME PROVENANCE GATE:
    Fails to compile if the benchmark artifact was generated from fixtures instead of live data.
    Ensures pre-publish checks never pass on dummy/test fixture data. -/
theorem empirical_data_is_live : checkAllLive = true := by
  native_decide

-- Print dependencies to audit for sorryAx / unproven axioms before publication.
#print axioms GraphPolicy.Validation.empirical_data_valid
#print axioms GraphPolicy.forbidden_induced_cannot_express_conditional_approval

end GraphPolicy.Audit
