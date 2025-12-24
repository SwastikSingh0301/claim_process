class PaymentsPublisher:
    """
    Abstraction for publishing claim processed events to a payments system.
    
    INTEGRATION PATTERN: Transactional Outbox
    
    Instead of directly calling payments service here, we use the outbox pattern:
    
    1. When claim is processed, an OutboxEvent is created in the SAME database 
       transaction as the claim data (see process_claim endpoint)
    
    2. A background worker (OutboxProcessor) polls the outbox table using:
       SELECT * FROM outbox_events 
       WHERE status = 'PENDING' 
       FOR UPDATE SKIP LOCKED
       
    3. Worker publishes events to message broker (Kafka/SQS/RabbitMQ)
    
    4. Payments service consumes from broker with idempotency protection
    
    FAILURE HANDLING:
    - If claim processing fails: transaction rolls back, no event created
    - If event creation fails: transaction rolls back, no claim persisted  
    - If publishing fails: event stays in outbox, worker retries with backoff
    - If payments service fails: message goes to DLQ, ops team alerted
    
    CONCURRENCY:
    - Multiple claim_process instances can run concurrently
    - FOR UPDATE SKIP LOCKED prevents race conditions in outbox polling
    - Each instance processes different events in parallel
    - Idempotency keys prevent duplicate payment processing
    
    NOTE: For full implementation see design doc in payments_integration_design.py
    """
    def publish_claim_processed(self, claim_id: str) -> None:
        raise NotImplementedError("Uses outbox pattern - see class docstring")