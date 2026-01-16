<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class FireDetected implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public array $fireDetectionData;

    public function __construct(array $fireDetectionData)
    {
        $this->fireDetectionData = $fireDetectionData;
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
        return 'fire.detected';
    }

    /**
     * Get the data to broadcast.
     */
    public function broadcastWith(): array
    {
        return $this->fireDetectionData;
    }
}
