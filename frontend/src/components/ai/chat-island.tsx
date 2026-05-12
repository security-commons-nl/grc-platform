'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { ChatPanel } from '@/components/ai/chat-panel';
import { api } from '@/lib/api-client';
import type { AgentConversationResponse } from '@/lib/api-types';

// Maps step number → agent name
const STEP_AGENT_MAP: Record<string, string> = {
  '1': 'commitment-agent',
  '2a': 'context-agent',
  '2b': 'scope-agent',
  '3a': 'governance-agent',
  '4': 'gap-agent',
  '5': 'register-agent',
  '6': 'controls-agent',
};

interface ChatIslandProps {
  stepNumber: string;
  executionId: string;
}

export function ChatIsland({ stepNumber, executionId }: ChatIslandProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const agentName = STEP_AGENT_MAP[stepNumber];

  const {
    data: conversation,
    mutate: mutateConversation,
  } = useSWR<AgentConversationResponse>(
    isOpen && agentName ? `/agents/conversation/${executionId}/${agentName}` : null,
    async () => {
      const conv = await api.agents.startConversation(agentName!, {
        step_execution_id: executionId,
      });
      return conv;
    },
  );

  if (!agentName) return null;

  async function handleOpen() {
    if (isOpen) {
      setIsOpen(false);
      return;
    }

    setIsStarting(true);
    setIsOpen(true);
    setIsStarting(false);
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={handleOpen}
        className={`fixed bottom-6 right-6 z-40 flex items-center gap-2 rounded-full px-4 py-3 shadow-lg transition-all ${
          isOpen
            ? 'bg-neutral-600 text-white'
            : 'bg-primary-600 text-white hover:bg-primary-700'
        }`}
      >
        <ChatBubbleLeftRightIcon className="h-5 w-5" />
        <span className="text-sm font-medium">
          {isStarting ? 'Laden...' : isOpen ? 'Sluit chat' : 'AI-assistent'}
        </span>
      </button>

      {/* Chat panel */}
      {isOpen && conversation && (
        <ChatPanel
          conversation={conversation}
          onClose={() => setIsOpen(false)}
          onUpdate={() => mutateConversation()}
        />
      )}
    </>
  );
}
