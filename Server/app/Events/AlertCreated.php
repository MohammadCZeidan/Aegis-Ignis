<?php

namespace App\Events;

use App\Models\Alert;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class AlertCreated implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public Alert $alert;

    public function __construct(Alert $alert)
    {
        $this->alert = $alert;
    }

    /**
     * Get the channels the event should broadcast on.
     */
    public function broadcastOn(): Channel
    {
        return new Channel('aegis-alerts');
    }

    /**
     * The event's broadcast name.
     */
    public function broadcastAs(): string
    {
        return 'alert.created';
    }

    /**
     * Get the data to broadcast.
     */
    public function broadcastWith(): array
    {
        return [
            'id' => $this->alert->id,
            'type' => $this->alert->type,
            'severity' => $this->alert->severity,
            'message' => $this->alert->message,
            'camera_id' => $this->alert->camera_id,
            'floor_id' => $this->alert->floor_id,
            'status' => $this->alert->status,
            'created_at' => $this->alert->created_at->toISOString(),
        ];
    }
}
