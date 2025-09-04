import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog";
import { Plus, MoreHorizontal, Edit3, Trash2, MessageSquare } from "lucide-react";
import { ChatSession } from "@/types/chat";
import { formatDistanceToNow } from "date-fns";

interface ChatSessionSelectorProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onCreateNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, newName: string) => void;
}

const ChatSessionSelector = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateNewChat,
  onDeleteSession,
  onRenameSession
}: ChatSessionSelectorProps) => {
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [sessionToRename, setSessionToRename] = useState<ChatSession | null>(null);
  const [newSessionName, setNewSessionName] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);



  const handleRenameClick = (session: ChatSession) => {
    setSessionToRename(session);
    setNewSessionName(session.name);
    setIsRenameDialogOpen(true);
  };

  const handleRenameSubmit = () => {
    if (sessionToRename && newSessionName.trim()) {
      onRenameSession(sessionToRename.id, newSessionName.trim());
      setIsRenameDialogOpen(false);
      setSessionToRename(null);
      setNewSessionName("");
    }
  };

  const activeSession = sessions.find(session => session.id === activeSessionId);

  return (
    <div className="flex items-center gap-2">
      {/* New Chat Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={onCreateNewChat}
        className="flex-shrink-0"
      >
        <Plus className="h-4 w-4 mr-1" />
      </Button>

      {/* Session Selector */}
      {sessions.length > 0 && (
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Select 
            value={activeSessionId || ""} 
            onValueChange={onSelectSession}
            onOpenChange={setIsDropdownOpen}
          >
            <SelectTrigger className="flex-1 min-w-0">
              <SelectValue placeholder="Select a chat session">
                {activeSession && (
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-3 w-3 flex-shrink-0" />
                    <span className="truncate">{activeSession.name}</span>
                  </div>
                )}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {sessions.map((session) => (
                <SelectItem key={session.id} value={session.id}>
                  <div className="flex items-center gap-2 w-full">
                    <MessageSquare className="h-3 w-3 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="truncate">{session.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatDistanceToNow(session.updatedAt, { addSuffix: true })}
                      </div>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Session Actions Dropdown */}
          {activeSession && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleRenameClick(activeSession)}>
                  <Edit3 className="h-4 w-4 mr-2" />
                  Rename
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => onDeleteSession(activeSession.id)}
                  className="text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      )}

      {/* Rename Dialog */}
      <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Chat Session</DialogTitle>
            <DialogDescription>
              Enter a new name for this chat session.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder="Enter new name"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleRenameSubmit();
                }
              }}
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setIsRenameDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleRenameSubmit}
                disabled={!newSessionName.trim()}
              >
                Rename
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatSessionSelector; 