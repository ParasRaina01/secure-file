import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Copy, Link as LinkIcon, Users } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { shareFile, createShareableLink } from '@/features/files/filesSlice'

interface ShareDialogProps {
  file: {
    id: string
    name: string
  }
  onClose: () => void
}

export const ShareDialog: React.FC<ShareDialogProps> = ({ file, onClose }) => {
  const dispatch = useDispatch()
  const { toast } = useToast()
  const [email, setEmail] = useState('')
  const [shareableLink, setShareableLink] = useState('')
  const [expirationDays, setExpirationDays] = useState('7')
  const [isLoading, setIsLoading] = useState(false)

  const handleShareWithUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await dispatch(shareFile({ fileId: file.id, email }))
      toast({
        title: "Success",
        description: "File shared successfully",
      })
      setEmail('')
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to share file",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateLink = async () => {
    setIsLoading(true)
    try {
      const response = await dispatch(createShareableLink({
        fileId: file.id,
        expirationDays: parseInt(expirationDays),
      }))
      setShareableLink(response.payload.link)
      toast({
        title: "Success",
        description: "Shareable link created",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create shareable link",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: "Success",
        description: "Link copied to clipboard",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy link",
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Share "{file.name}"</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <h3 className="font-medium">Share with user</h3>
            </div>
            <form onSubmit={handleShareWithUser} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Sharing..." : "Share"}
              </Button>
            </form>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <LinkIcon className="h-5 w-5" />
              <h3 className="font-medium">Create shareable link</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="expiration">Link expiration</Label>
                <select
                  id="expiration"
                  className="w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={expirationDays}
                  onChange={(e) => setExpirationDays(e.target.value)}
                >
                  <option value="1">1 day</option>
                  <option value="7">7 days</option>
                  <option value="30">30 days</option>
                </select>
              </div>
              <Button
                onClick={handleCreateLink}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? "Creating..." : "Create link"}
              </Button>
            </div>

            {shareableLink && (
              <div className="space-y-2">
                <Label>Shareable link</Label>
                <div className="flex space-x-2">
                  <Input
                    value={shareableLink}
                    readOnly
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => copyToClipboard(shareableLink)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 