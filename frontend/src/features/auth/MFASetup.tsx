import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { enableMFA, verifyMFA } from '@/features/auth/authSlice'

const MFASetup: React.FC = () => {
  const dispatch = useDispatch()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [step, setStep] = useState<'initial' | 'verify' | 'complete'>('initial')

  const handleEnableMFA = async () => {
    setIsLoading(true)
    try {
      const response = await dispatch(enableMFA())
      if (response.meta.requestStatus === 'fulfilled') {
        setQrCode(response.payload.qrCode)
        setSecret(response.payload.secret)
        setStep('verify')
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to enable MFA. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyMFA = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const response = await dispatch(verifyMFA({ code: verificationCode, secret }))
      if (response.meta.requestStatus === 'fulfilled') {
        setBackupCodes(response.payload.backupCodes)
        setStep('complete')
        toast({
          title: "Success",
          description: "MFA enabled successfully",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Invalid verification code. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-[600px] space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Two-Factor Authentication</h2>
        <p className="text-muted-foreground">
          Enhance your account security by enabling two-factor authentication
        </p>
      </div>

      {step === 'initial' && (
        <div className="space-y-4">
          <p>
            Two-factor authentication adds an extra layer of security to your account.
            When enabled, you'll need to enter a code from your authenticator app
            in addition to your password when signing in.
          </p>
          <Button onClick={handleEnableMFA} disabled={isLoading}>
            {isLoading ? "Setting up..." : "Enable 2FA"}
          </Button>
        </div>
      )}

      {step === 'verify' && (
        <div className="space-y-6">
          <div className="space-y-4">
            <p>
              1. Install an authenticator app like Google Authenticator or Authy
              on your mobile device.
            </p>
            <p>
              2. Scan this QR code with your authenticator app:
            </p>
            <div className="flex justify-center">
              <img src={qrCode} alt="QR Code" className="h-48 w-48" />
            </div>
            <p>
              Can't scan the QR code? Use this secret key instead:
              <code className="mx-2 rounded bg-muted px-2 py-1">{secret}</code>
            </p>
          </div>

          <form onSubmit={handleVerifyMFA} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="verificationCode">Verification Code</Label>
              <Input
                id="verificationCode"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter 6-digit code"
                maxLength={6}
                required
              />
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Verifying..." : "Verify"}
            </Button>
          </form>
        </div>
      )}

      {step === 'complete' && (
        <div className="space-y-6">
          <div className="rounded-lg border p-4">
            <h3 className="font-semibold">Backup Codes</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Save these backup codes in a secure place. You can use them to access
              your account if you lose your authenticator device.
            </p>
            <div className="grid grid-cols-2 gap-2">
              {backupCodes.map((code, index) => (
                <code key={index} className="rounded bg-muted px-2 py-1 text-sm">
                  {code}
                </code>
              ))}
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            ⚠️ These codes will only be shown once. Make sure to save them now.
          </p>
        </div>
      )}
    </div>
  )
}

export default MFASetup 