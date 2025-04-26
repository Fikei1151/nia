import logging
import json
from typing import Any, AsyncGenerator, List, Optional, Sequence, Tuple, Dict, Iterable
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple
from langchain_core.load import dumps, loads
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat_history import ChatHistory
from app.core.db import AsyncSessionFactory

logger = logging.getLogger(__name__)

class PostgresCheckpointSaver(BaseCheckpointSaver):
    """
    PostgreSQL Checkpoint Saver implementing BaseCheckpointSaver interface.
    Serializes both checkpoint and metadata before saving to JSON columns.
    """

    def __init__(self):
        super().__init__()
        if not AsyncSessionFactory:
            raise RuntimeError("Database session factory is not initialized. Check DATABASE_URL.")
        self.session_factory = AsyncSessionFactory

    async def aget_tuple(self, config: Dict) -> Optional[CheckpointTuple]:
        """Load the checkpoint tuple for the given config."""
        thread_id = config["configurable"]["thread_id"]
        async with self.session_factory() as session:
            stmt = select(ChatHistory).where(ChatHistory.thread_id == thread_id).order_by(ChatHistory.updated_at.desc()).limit(1)
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                logger.debug(f"Checkpoint found for thread_id: {thread_id}")
                try:
                    # Load checkpoint data
                    raw_checkpoint_data = record.checkpoint_blob
                    if not isinstance(raw_checkpoint_data, (dict, list)):
                         logger.warning(f"Checkpoint data from DB is not dict/list, attempting json.loads. Type: {type(raw_checkpoint_data)}")
                         raw_checkpoint_data = json.loads(str(raw_checkpoint_data))
                    checkpoint_data = loads(json.dumps(raw_checkpoint_data))

                    # Load metadata data
                    raw_metadata = record.metadata_blob
                    if not isinstance(raw_metadata, dict):
                         logger.warning(f"Metadata from DB is not a dict, using empty dict. Type: {type(raw_metadata)}")
                         loaded_metadata = {}
                    else:
                         # Metadata should already be JSON serializable dict from DB
                         loaded_metadata = raw_metadata
                         # Optional: If metadata needs deserialization (unlikely if saved correctly)
                         # loaded_metadata = loads(json.dumps(raw_metadata))

                    return CheckpointTuple(
                        config=config,
                        checkpoint=checkpoint_data,
                        metadata=loaded_metadata,
                        parent_config=None
                    )
                except Exception as e:
                    logger.exception(f"Failed to deserialize checkpoint/metadata from DB for thread_id {thread_id}: {e}")
                    return None
            else:
                logger.debug(f"No checkpoint found for thread_id: {thread_id}")
                return None

    async def alist(
        self,
        config: Optional[Dict] = None,
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[CheckpointTuple, None]:
         # ... (โค้ดเดิม ไม่ต้องแก้) ...
        if config and "configurable" in config and "thread_id" in config["configurable"]:
             checkpoint_tuple = await self.aget_tuple(config)
             if checkpoint_tuple:
                  yield checkpoint_tuple
        else:
            logger.warning("Listing all checkpoints or complex filtering is not fully implemented.")
            if False: yield

    async def aput(
        self,
        config: Dict,
        checkpoint: Dict,
        metadata: Dict,
        task_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Save the checkpoint and its metadata for the given config."""
        logger.debug(f"aput called with config: {config}, metadata: {metadata}, task_inputs: {task_inputs is not None}")
        thread_id = config["configurable"]["thread_id"]
        platform = config.get("configurable", {}).get("platform", metadata.get("platform", "web"))
        user_id = config.get("configurable", {}).get("user_id", metadata.get("user_id", None))
        project_id = config.get("configurable", {}).get("project_id", metadata.get("project_id", None))

        try:
            # --- Serialize checkpoint ---
            cp_json_string: str = dumps(checkpoint)
            serializable_checkpoint: Dict | List = json.loads(cp_json_string)

            # --- Serialize metadata ---
            md_json_string: str = dumps(metadata) # <--- Serialize metadata ด้วย
            serializable_metadata: Dict | List = json.loads(md_json_string) # <--- แปลงกลับเป็น dict/list

        except Exception as e:
            logger.exception(f"Failed to serialize checkpoint or metadata for thread_id {thread_id}: {e}")
            raise

        async with self.session_factory() as session:
            async with session.begin():
                stmt_delete = delete(ChatHistory).where(ChatHistory.thread_id == thread_id)
                await session.execute(stmt_delete)
                new_record = ChatHistory(
                    thread_id=thread_id,
                    project_id=project_id,
                    platform=platform,
                    user_id=user_id,
                    checkpoint_blob=serializable_checkpoint,
                    metadata_blob=serializable_metadata # <--- บันทึก metadata ที่ serialize แล้ว
                )
                session.add(new_record)
                logger.debug(f"Checkpoint and metadata saved/updated for thread_id: {thread_id}")
            await session.commit()
        return config

    async def aput_writes(
        self,
        config: Dict,
        writes: Iterable[Tuple[str, Any]],
        task_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict:
         # ... (โค้ดเดิม ไม่ต้องแก้) ...
        thread_id = config["configurable"]["thread_id"]
        logger.warning(f"aput_writes called for thread_id {thread_id}, but this saver doesn't store intermediate writes separately.")
        return config