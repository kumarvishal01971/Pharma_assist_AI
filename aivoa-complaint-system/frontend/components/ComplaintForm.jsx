import { useSelector, useDispatch } from 'react-redux'
import { setField, resetForm, saveComplaint } from '../store/complaintSlice'

const SEVERITY_OPTIONS = ['Critical', 'Major', 'Minor']
const PRIORITY_OPTIONS = ['High', 'Medium', 'Low']

function Field({ id, label, unit, children }) {
  return (
    <div className="field">
      <label htmlFor={id}>
        {label} {unit && <span className="unit">({unit})</span>}
      </label>
      {children}
    </div>
  )
}

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const { form, status, missingFields, extractionStatus, saveStatus, savedComplaintId } =
    useSelector((s) => s.complaint)

  const aiFilled = extractionStatus === 'succeeded'
  const isMissing = (field) => missingFields.includes(field)

  const onChange = (field) => (e) => dispatch(setField({ field, value: e.target.value }))

  const inputClass = (field) => (aiFilled && form[field] ? 'ai-filled' : '')

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Log Customer Complaint</h2>
          <div className="panel-sub">API &amp; FDF Quality Assurance Module</div>
        </div>
        <span className={`status-badge ${savedComplaintId ? 'saved' : 'pending'}`}>
          {savedComplaintId ? 'Saved' : status}
        </span>
      </div>

      <div className="form-body">
        {/* Section 1 */}
        <div className="form-section">
          <div className="section-rail">
            <div className="dot">1</div>
            <div className="line" />
          </div>
          <div className="section-content">
            <div className="section-title">Origin &amp; Customer Details</div>
            <div className="field-grid">
              <Field id="complaint_source" label="Complaint Source">
                <input
                  id="complaint_source"
                  className={inputClass('complaint_source')}
                  value={form.complaint_source}
                  onChange={onChange('complaint_source')}
                  placeholder="e.g. Email, Phone, Portal"
                />
              </Field>
              <Field id="customer_name" label="Customer Name">
                <input
                  id="customer_name"
                  className={inputClass('customer_name')}
                  value={form.customer_name}
                  onChange={onChange('customer_name')}
                />
              </Field>
            </div>
          </div>
        </div>

        {/* Section 2 */}
        <div className="form-section">
          <div className="section-rail">
            <div className="dot">2</div>
            <div className="line" />
          </div>
          <div className="section-content">
            <div className="section-title">Product &amp; Batch Identification</div>
            <div className="field-grid">
              <Field id="product_name" label="Product Name">
                <input
                  id="product_name"
                  className={inputClass('product_name')}
                  value={form.product_name}
                  onChange={onChange('product_name')}
                />
              </Field>
              <Field id="product_strength_grade" label="Product Strength/Grade">
                <input
                  id="product_strength_grade"
                  className={inputClass('product_strength_grade')}
                  value={form.product_strength_grade}
                  onChange={onChange('product_strength_grade')}
                />
              </Field>
              <Field id="batch_lot_number" label="Batch/Lot Number">
                <input
                  id="batch_lot_number"
                  className={inputClass('batch_lot_number')}
                  value={form.batch_lot_number}
                  onChange={onChange('batch_lot_number')}
                />
              </Field>
              <Field id="manufacturing_date" label="Manufacturing Date">
                <input
                  id="manufacturing_date"
                  type="date"
                  className={inputClass('manufacturing_date')}
                  value={form.manufacturing_date}
                  onChange={onChange('manufacturing_date')}
                />
              </Field>
              <Field id="expiry_date" label="Expiry Date">
                <input
                  id="expiry_date"
                  type="date"
                  className={inputClass('expiry_date')}
                  value={form.expiry_date}
                  onChange={onChange('expiry_date')}
                />
              </Field>
              <Field id="quantity_affected" label="Quantity Affected" unit="kg">
                <input
                  id="quantity_affected"
                  type="number"
                  className={inputClass('quantity_affected')}
                  value={form.quantity_affected}
                  onChange={onChange('quantity_affected')}
                />
              </Field>
            </div>
          </div>
        </div>

        {/* Section 3 */}
        <div className="form-section">
          <div className="section-rail">
            <div className="dot">3</div>
            <div className="line" />
          </div>
          <div className="section-content">
            <div className="section-title">Complaint Details</div>
            <div className="field-grid">
              <Field id="complaint_type" label="Complaint Type">
                <input
                  id="complaint_type"
                  className={inputClass('complaint_type')}
                  value={form.complaint_type}
                  onChange={onChange('complaint_type')}
                />
              </Field>
              <Field id="complaint_date" label="Complaint Date">
                <input
                  id="complaint_date"
                  type="date"
                  className={inputClass('complaint_date')}
                  value={form.complaint_date}
                  onChange={onChange('complaint_date')}
                />
              </Field>
            </div>
            <div className="field-grid single" style={{ marginTop: 12 }}>
              <Field id="detailed_description" label="Detailed Complaint Description">
                <textarea
                  id="detailed_description"
                  className={inputClass('detailed_description')}
                  value={form.detailed_description}
                  onChange={onChange('detailed_description')}
                />
              </Field>
            </div>
            {isMissing('detailed_description') && (
              <div className="field-missing">Flagged as missing by the AI completeness check.</div>
            )}
          </div>
        </div>

        {/* Section 4 */}
        <div className="form-section">
          <div className="section-rail">
            <div className="dot">4</div>
          </div>
          <div className="section-content">
            <div className="section-title">Initial Assessment &amp; Priority</div>
            <div className="field-grid">
              <Field id="initial_severity" label="Initial Severity">
                <select
                  id="initial_severity"
                  className={inputClass('initial_severity')}
                  value={form.initial_severity}
                  onChange={onChange('initial_severity')}
                >
                  <option value="">Select...</option>
                  {SEVERITY_OPTIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </Field>
              <Field id="priority" label="Priority">
                <select
                  id="priority"
                  className={inputClass('priority')}
                  value={form.priority}
                  onChange={onChange('priority')}
                >
                  <option value="">Select...</option>
                  {PRIORITY_OPTIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </Field>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn btn-secondary" onClick={() => dispatch(resetForm())}>
            ↺ Reset Form
          </button>
          <button
            className="btn btn-primary"
            disabled={saveStatus === 'loading'}
            onClick={() => dispatch(saveComplaint())}
          >
            {saveStatus === 'loading' ? 'Saving...' : '🗎 Save Complaint'}
          </button>
        </div>
      </div>
    </section>
  )
}
