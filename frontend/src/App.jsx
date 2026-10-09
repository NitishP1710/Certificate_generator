import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_URL = '/api'
const defaultTemplate = {
  name: 'Course Certificate',
  title: 'Certificate of Completion',
  content: 'This certificate is proudly presented to\n\n{{name}}\n\nfor successfully completing\n\n{{course}}\n\non\n\n{{date}}',
}

const extractPlaceholders = (content = '') => {
  const matches = [...content.matchAll(/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g)]
  return [...new Set(matches.map((match) => match[1]))]
}

function App() {
  const [templates, setTemplates] = useState([])
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [templateForm, setTemplateForm] = useState(defaultTemplate)
  const [currentFile, setCurrentFile] = useState(null)
  const [validationResult, setValidationResult] = useState(null)
  const [activeJobId, setActiveJobId] = useState(null)
  const [activeJob, setActiveJob] = useState(null)
  const [jobCertificates, setJobCertificates] = useState([])
  const [jobs, setJobs] = useState([])
  const [statusMessage, setStatusMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const placeholders = useMemo(() => extractPlaceholders(templateForm.content), [templateForm.content])

  useEffect(() => {
    fetchTemplates()
  }, [])

  useEffect(() => {
    if (!activeJobId) {
      return undefined
    }

    const pollJob = async () => {
      const response = await fetch(`${API_URL}/generation/${activeJobId}`)
      if (!response.ok) {
        return
      }
      const job = await response.json()
      setActiveJob(job)
      setJobs((previousJobs) => {
        const nextJobs = previousJobs.filter((item) => item.id !== job.id)
        return [job, ...nextJobs]
      })

      const certResponse = await fetch(`${API_URL}/generation/${activeJobId}/certificates`)
      if (certResponse.ok) {
        const certificates = await certResponse.json()
        setJobCertificates(certificates)
      }
    }

    pollJob()
    const timer = setInterval(pollJob, 2500)
    return () => clearInterval(timer)
  }, [activeJobId])

  const fetchTemplates = async () => {
    const response = await fetch(`${API_URL}/templates`)
    const data = await response.json()
    setTemplates(data)
    if (data.length > 0) {
      const firstTemplate = data[0]
      setSelectedTemplateId(String(firstTemplate.id))
      setTemplateForm({
        name: firstTemplate.name,
        title: firstTemplate.title || '',
        content: firstTemplate.content,
      })
    }
  }

  const loadTemplate = (templateId) => {
    const selectedTemplate = templates.find((template) => String(template.id) === String(templateId))
    if (!selectedTemplate) {
      return
    }
    setSelectedTemplateId(String(selectedTemplate.id))
    setTemplateForm({
      name: selectedTemplate.name,
      title: selectedTemplate.title || '',
      content: selectedTemplate.content,
    })
  }

  const handleCreateTemplate = async (event) => {
    event.preventDefault()
    setIsSubmitting(true)
    try {
      const response = await fetch(`${API_URL}/templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: templateForm.name,
          title: templateForm.title,
          content: templateForm.content,
        }),
      })

      if (!response.ok) {
        throw new Error('Template could not be saved.')
      }

      const createdTemplate = await response.json()
      setTemplates((previous) => [createdTemplate, ...previous])
      setSelectedTemplateId(String(createdTemplate.id))
      setStatusMessage(`Template ${createdTemplate.name} saved successfully.`)
    } catch (error) {
      setStatusMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const validateFile = async (file) => {
    if (!selectedTemplateId) {
      setStatusMessage('Select or create a template before validating the workbook.')
      return
    }

    const body = new FormData()
    body.append('file', file)

    const response = await fetch(`${API_URL}/templates/${selectedTemplateId}/validate-excel`, {
      method: 'POST',
      body,
    })

    const result = await response.json()
    setValidationResult(result)
    return result
  }

  const handleFileSelection = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    setCurrentFile(file)
    setStatusMessage(`Validating ${file.name}...`)
    await validateFile(file)
    setStatusMessage('Excel validation complete.')
  }

  const handleGenerate = async () => {
    if (!selectedTemplateId || !currentFile) {
      setStatusMessage('Choose a template and Excel file before generating certificates.')
      return
    }

    const validation = await validateFile(currentFile)
    if (!validation || !validation.valid) {
      setStatusMessage('Validation failed. Fix these errors before generating certificates.')
      return
    }

    const body = new FormData()
    body.append('template_id', String(selectedTemplateId))
    body.append('file', currentFile)

    const response = await fetch(`${API_URL}/generation`, {
      method: 'POST',
      body,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData?.detail?.message || 'Generation request failed.')
    }

    const payload = await response.json()
    const jobResponse = await fetch(`${API_URL}/generation/${payload.job_id}`)
    const job = await jobResponse.json()
    setJobs((previousJobs) => [job, ...previousJobs.filter((item) => item.id !== job.id)])
    setActiveJobId(job.id)
    setActiveJob(job)
    setStatusMessage(`Job #${job.id} started. Progress is being tracked live.`)
  }

  const handleDownload = (certificateId) => {
    window.open(`${API_URL}/certificates/${certificateId}`, '_blank')
  }

  const progressPercent = activeJob
    ? Math.round(((Number(activeJob.success_count || 0) + Number(activeJob.failed_count || 0)) / Math.max(Number(activeJob.total_count || 0), 1)) * 100)
    : 0

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Certificate system</p>
          <h1>Bulk Certificate Generator</h1>
        </div>
        <div className="status-pill">{statusMessage || 'Ready for work'}</div>
      </header>

      <main className="main-grid">
        <aside className="panel sidebar-panel">
          <div className="panel-header">
            <h2>Templates</h2>
          </div>
          <div className="template-list">
            {templates.length === 0 ? (
              <p className="empty-state">No templates yet.</p>
            ) : (
              templates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  className={`template-item ${String(template.id) === String(selectedTemplateId) ? 'selected' : ''}`}
                  onClick={() => loadTemplate(template.id)}
                >
                  <strong>{template.name}</strong>
                  <span>{template.placeholders?.length || 0} placeholders</span>
                </button>
              ))
            )}
          </div>

          <div className="panel-header jobs-header">
            <h2>Recent jobs</h2>
          </div>
          <div className="job-list">
            {jobs.length === 0 ? (
              <p className="empty-state">No generation jobs yet.</p>
            ) : (
              jobs.map((job) => (
                <button
                  key={job.id}
                  type="button"
                  className={`job-item ${String(job.id) === String(activeJobId) ? 'selected' : ''}`}
                  onClick={() => setActiveJobId(job.id)}
                >
                  <span>Job #{job.id}</span>
                  <strong>{job.status}</strong>
                  <small>
                    {job.success_count}/{job.total_count} completed
                  </small>
                </button>
              ))
            )}
          </div>
        </aside>

        <section className="content-stack">
          <form className="panel form-panel" onSubmit={handleCreateTemplate}>
            <div className="panel-header">
              <h2>Create template</h2>
            </div>

            <label>
              Template name
              <input
                value={templateForm.name}
                onChange={(event) => setTemplateForm((current) => ({ ...current, name: event.target.value }))}
                placeholder="Award Template"
              />
            </label>

            <label>
              Certificate title
              <input
                value={templateForm.title}
                onChange={(event) => setTemplateForm((current) => ({ ...current, title: event.target.value }))}
                placeholder="Certificate of Completion"
              />
            </label>

            <label>
              Template content
              <textarea
                rows={8}
                value={templateForm.content}
                onChange={(event) => setTemplateForm((current) => ({ ...current, content: event.target.value }))}
                placeholder="This certificate is proudly presented to..."
              />
            </label>

            <div className="placeholder-chip-set">
              {placeholders.length === 0 ? (
                <span className="placeholder-empty">No placeholders detected yet</span>
              ) : (
                placeholders.map((placeholder) => (
                  <span key={placeholder} className="placeholder-chip">
                    {'{{'}
                    {placeholder}
                    {'}}'}
                  </span>
                ))
              )}
            </div>

            <button type="submit" className="primary-button" disabled={isSubmitting}>
              {isSubmitting ? 'Saving template...' : 'Save template'}
            </button>
          </form>

          <div className="panel upload-panel">
            <div className="panel-header">
              <h2>Upload Excel</h2>
            </div>

            <label className="select-row">
              Template
              <select value={selectedTemplateId} onChange={(event) => loadTemplate(event.target.value)}>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="file-picker">
              <input type="file" accept=".xlsx,.xls" onChange={handleFileSelection} />
            </label>

            {validationResult && (
              <div className={`validation-box ${validationResult.valid ? 'valid' : 'invalid'}`}>
                <p>
                  <strong>{validationResult.valid_rows}</strong> valid rows
                </p>
                <p>
                  <strong>{validationResult.invalid_rows}</strong> invalid rows
                </p>
                {validationResult.errors.length > 0 ? (
                  <ul>
                    {validationResult.errors.map((error, index) => (
                      <li key={`${error.row ?? 'header'}-${error.field ?? 'field'}-${index}`}>
                        {error.row ? `Row ${error.row} → ` : ''}
                        {error.field ? `${error.field}: ` : ''}
                        {error.message}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>Validation passed. No structural or required-value issues found.</p>
                )}
              </div>
            )}

            <button type="button" className="primary-button" onClick={handleGenerate}>
              Start generation
            </button>
          </div>
        </section>

        <section className="panel status-panel">
          <div className="panel-header">
            <h2>Generation status</h2>
          </div>

          {activeJob ? (
            <>
              <div className="job-summary">
                <div>
                  <span>Job #{activeJob.id}</span>
                  <strong>{activeJob.status}</strong>
                </div>
                <div>
                  <span>Total</span>
                  <strong>{activeJob.total_count}</strong>
                </div>
                <div>
                  <span>Successful</span>
                  <strong>{activeJob.success_count}</strong>
                </div>
                <div>
                  <span>Failed</span>
                  <strong>{activeJob.failed_count}</strong>
                </div>
              </div>

              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
              </div>
              <p className="progress-meta">
                {Math.round(progressPercent)}% complete • {Number(activeJob.success_count || 0) + Number(activeJob.failed_count || 0)} / {Number(activeJob.total_count || 0)} completed
              </p>

              <div className="certificates-box">
                {jobCertificates.length === 0 ? (
                  <p className="empty-state">No certificate records yet.</p>
                ) : (
                  jobCertificates.map((certificate) => (
                    <div key={certificate.id} className="certificate-row">
                      <div>
                        <strong>Row {certificate.row_number}</strong>
                        <span>{certificate.status}</span>
                      </div>
                      {certificate.error_message && <small>{certificate.error_message}</small>}
                      {certificate.status === 'SUCCESS' && (
                        <button type="button" onClick={() => handleDownload(certificate.id)}>
                          Download
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <p className="empty-state">Choose a job from the sidebar to inspect the live status.</p>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
